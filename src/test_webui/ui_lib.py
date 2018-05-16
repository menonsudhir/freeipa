try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.common.exceptions import NoSuchElementException
    from selenium.common.exceptions import InvalidElementStateException
    from selenium.common.exceptions import StaleElementReferenceException
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.by import By
except ImportError as e:
    raise exit("Python Selenium module is not "
               "installed : %s" % (e.args[0]))
try:
    from pyvirtualdisplay import Display
except ImportError as e:
    raise exit("Pyvirtualdisplay module is not "
               "installed : %s" % (e.args[0]))
import os
import pytest
import yaml
import time


class ui_driver(object):
    def __init__(self, host):
        self.host = host
        self.display = Display(visible=0, size=(800, 600))
        self.display.start()

    def setup(self, driver=None, config=None):
        self.request_timeout = 30
        self.driver = driver
        self.config = {}
        self.display = None
        self.get_config()
        self.driver = self.get_driver()

    def teardown(self):
        """
        Cleanup all driver
        """
        self.driver.quit()
        if self.display:
            self.display.stop()

    def get_config(self):
        """
        Get Web UI related configurations and create config dictionary
        """
        self.config['ipa_server'] = self.host.hostname
        self.config['ipa_passwd'] = self.host.config.admin_pw
        self.config['ipa_admin'] = self.host.config.admin_id
        self.config['browser'] = self.host.config.browser
        self.config['virtualdisplay'] = self.host.config.virtualdisplay
        self.config['untrusted_certs'] = self.host.config.untrusted_certs

    def get_base_url(self):
        """
        Create IPA url from ip or fqdn
        """
        host = self.config.get('ipa_server')
        if not host:
            pytest.xfail("IPA server hostname not configured")
        return "http://%s/ipa/ui" % host

    def get_driver(self):
        """
        Get WebDriver according to configuration
        """
        browser = self.config['browser']
        options = None
        try:
            if browser == 'firefox':
                if 'ff_profile' in self.config:
                    options = webdriver.FirefoxProfile(self.config['ff_profile'])
                else:
                    fp = webdriver.FirefoxProfile()
                    fp.set_preference("browser.download.folderList", 2)
                    fp.set_preference("browser.download.manager.showWhenStarting", False)
                    fp.set_preference("browser.download.dir", os.getcwd())
                    fp.set_preference("browser.helperApps.neverAsk.saveToDisk",
                                      "application/octet-stream")
                    untrusted_certs = self.config.get('untrusted_certs', 'False')
                    if untrusted_certs == 'True':
                        fp.accept_untrusted_certs = True
                    elif untrusted_certs == 'False':
                        fp.accept_untrusted_certs = False
                    options = fp
                driver = webdriver.Firefox(firefox_profile=options)
            elif browser == 'chrome':
                options = ChromeOptions()
                options.binary_location = multihost.master.config.chrome_browser
                driver = webdriver.Chrome(chrome_options=options)
        except RuntimeError as e:
            pytest.xfail("Error while creating selenium webdriver : %s" % e.args[0])
        return driver

    def init_app(self, username=None, password=None):
        """
        initialize and load application
        """
        self.load()
        self.wait(0.5)
        self.login(username, password)

    def load(self):
        """
        Navigate to first page of IPA and wait for asests to load
        """
        self.driver.get(self.get_base_url())
        runner = self
        WebDriverWait(self.driver, self.request_timeout).until(lambda d: runner.files_loaded())

    def files_loaded(self):
        """
        Test if dependencies were loaded. (Checks if UI has been rendered)
        """
        indicator = self.find(".global-activity-indicator", By.CSS_SELECTOR)
        return indicator is not None

    def wait(self, seconds=0.2):
        """
        Wait for specified time in seconds
        """
        time.sleep(seconds)

    def wait_for_request(self, implicit=0.2, n=1, d=0):
        """
        Wait for AJAX request to finish
        """
        runner = self

        for i in range(n):
            self.wait(implicit)
            WebDriverWait(self.driver,
                          self.request_timeout).until_not(lambda d: runner.has_active_request())
            self.wait()
        self.wait(d)

    def has_active_request(self):
        """
        Check if there is running AJAX request
        """
        global_indicators = self.find(".global-activity-indicator", By.CSS_SELECTOR, many=True)
        for el in global_indicators:
            try:
                if not self.has_class(el, 'closed'):
                    return True
            except StaleElementReferenceException:
                continue
        return False

    def has_class(self, el, cls):
        """
        Check if el has CSS class
        """
        return cls in el.get_attribute("class").split()

    def find(self, expression, by='id', context=None, many=False, strict=False):
        """
        Helper which calls selenium find_element_by_xxx methods.

        expression: search expression
        by: selenium.webdriver.common.by
        context: element to search on. Default: driver
        many: all matching elements
        strict: error out when element is not found

        Returns None instead of raising exception when element is not found.
        """

        assert expression, 'expression is missing'

        if context is None:
            context = self.driver

        if not many:
            method_name = 'find_element'
        else:
            method_name = 'find_elements'

        try:
            func = getattr(context, method_name)
            result = func(by, expression)
        except NoSuchElementException:
            if strict:
                raise
            else:
                result = None

        return result

    def get_login_screen(self):
        """
        Get reference of login screen
        """
        return self.find('rcue-login-screen', 'id')

    def logged_in(self):
        """
        Check if user is logged in
        """
        login_as = self.find('loggedinas', 'class name')
        visible_name = len(login_as.text) > 0
        logged_in = not self.login_screen_visible() and visible_name
        return logged_in

    def login_screen_visible(self):
        """
        Check if login screen is visible
        """
        screen = self.get_login_screen()
        return screen and screen.is_displayed()

    def login(self, login=None, password=None, new_password=None):
        """
        Log in if user is not logged in.
        """
        self.wait_for_request(n=2)
        if not self.logged_in():

            if not login:
                login = self.config['ipa_admin']
            if not password:
                password = self.config['ipa_passwd']
            if not new_password:
                new_password = password

            auth = self.get_login_screen()
            login_tb = self.find("//input[@type='text'][@name='username']", 'xpath', auth, strict=True)
            psw_tb = self.find("//input[@type='password'][@name='password']", 'xpath', auth, strict=True)
            login_tb.send_keys(login)
            psw_tb.send_keys(password)
            psw_tb.send_keys(Keys.RETURN)
            self.wait(0.5)
            self.wait_for_request(n=2)

            # reset password if needed
            newpw_tb = self.find("//input[@type='password'][@name='new_password']", 'xpath', auth)
            verify_tb = self.find("//input[@type='password'][@name='verify_password']", 'xpath', auth)
            if newpw_tb and newpw_tb.is_displayed():
                newpw_tb.send_keys(new_password)
                verify_tb.send_keys(new_password)
                verify_tb.send_keys(Keys.RETURN)
                self.wait(0.5)
                self.wait_for_request(n=2)

    def logout(self):
        """
        Logout of IPA application
        """
        self.profile_menu_action('logout')
        self.driver.quit()

    def profile_menu_action(self, name):
        """
        Execute action from profile menu
        """
        menu_toggle = self.find('[name=profile-menu] > a', By.CSS_SELECTOR)
        menu_toggle.click()
        s = "[name=profile-menu] a[href='#%s']" % name
        btn = self.find(s, By.CSS_SELECTOR, strict=True)
        btn.click()
        # action is usually followed by opening a dialog, add wait to compensate
        # possible dialog transition effect
        self.wait(0.5)

    def add_record(self, entity, data, facet='search', facet_btn='add',
                   dialog_btn='add', delete=False, pre_delete=True,
                   dialog_name='add', navigate=True):
        """
        Add records.

        Expected data format:
        {
            'pkey': 'key',
            add: [
                ('widget_type', 'key', 'value'),
                ('widget_type', 'key2', 'value2'),
            ],
        }
        """
        pkey = data['pkey']

        if navigate:
            self.navigate_to_entity(entity, facet)

        # check facet
        self.assert_facet(entity, facet)

        # delete if exists, ie. from previous test fail
        if pre_delete:
            self.delete_record(pkey, data.get('del'))

        # current row count
        self.wait_for_request(0.5)
        count = len(self.get_rows())

        # open add dialog
        self.assert_no_dialog()
        self.facet_button_click(facet_btn)
        self.assert_dialog(dialog_name)

        # fill dialog
        self.fill_fields(data['add'])

        # confirm dialog
        self.dialog_button_click(dialog_btn)
        self.wait_for_request()
        self.wait_for_request()

        # check expected error/warning/info
        expected = ['error_4304_info']
        dialog_info = self.get_dialog_info()
        if dialog_info and dialog_info['name'] in expected:
            self.dialog_button_click('ok')
            self.wait_for_request()

        # check for error
        self.assert_no_error_dialog()
        self.wait_for_request()
        self.wait_for_request(0.4)

        # check if table has more rows
        new_count = len(self.get_rows())
        # adjust because of paging
        expected = count + 1
        if count == 20:
            expected = 20
        self.assert_row_count(expected, new_count)

        # delete record
        if delete:
            self.delete_record(pkey)
            new_count = len(self.get_rows())
            self.assert_row_count(count, new_count)

    def assert_facet(self, entity, facet=None):
        """
        Assert that current facet is correct
        """
        info = self.get_facet_info()
        if facet is not None:
            assert info["name"] == facet, "Invalid facet. Expected: %s, Got: %s " % (facet, info["name"])
        assert info["entity"] == entity, "Invalid entity. Expected: %s, Got: %s " % (entity, info["entity"])

    def assert_undo_button(self, field, visible=True, parent=None):
        """
        Assert that undo button is or is not visible
        """
        undos = self.get_undo_buttons(field, parent)
        state = False
        for undo in undos:
            if undo.is_displayed():
                state = True
                break
        if visible:
            assert state, "Undo button not visible. Field: %s" % field
        else:
            assert not state, "Undo button visible. Field: %s" % field

    def assert_visible(self, selector, parent=None, negative=False):
        """
        Assert that element defined by selector is visible
        """
        if not parent:
            parent = self.get_form()
        el = self.find(selector, By.CSS_SELECTOR, parent, strict=True)
        visible = el.is_displayed()
        if negative:
            assert not visible, "Element visible: %s" % selector
        else:
            assert visible, "Element not visible: %s" % selector

    def assert_button_enabled(self, name, context_selector=None, enabled=True):
        """
        Assert that button is enabled or disabled (expects that element will be
        <button>)
        """
        s = ""
        if context_selector:
            s = context_selector
        s += "button[name=%s]" % name
        facet = self.get_facet()
        btn = self.find(s, By.CSS_SELECTOR, facet, strict=True)
        valid = enabled == btn.is_enabled()
        assert btn.is_displayed(), 'Button is not displayed'
        assert valid, 'Button (%s) has incorrect enabled state (enabled==%s).' % (s, enabled)

    def assert_facet_button_enabled(self, name, enabled=True):
        """
        Assert that facet button is enabled or disabled
        """
        self.assert_button_enabled(name, ".facet-controls ", enabled)

    def assert_table_button_enabled(self, name, table_name, enabled=True):
        """
        Assert that button in table is enabled/disabled
        """
        s = "table[name='%s'] " % table_name
        self.assert_button_enabled(name, s, enabled)

    def delete_record(self, pkeys, fields=None, parent=None, table_name=None):
        """
        Delete records with given pkeys in currently opened search table.
        """
        if type(pkeys) is not list:
            pkeys = [pkeys]

        # select
        selected = False
        for pkey in pkeys:
            delete = self.has_record(pkey, parent, table_name)
            if delete:
                self.select_record(pkey, parent, table_name)
                selected = True

        # exec and confirm
        if selected:
            if table_name and parent:
                s = self.get_table_selector(table_name)
                table = self.find(s, By.CSS_SELECTOR, parent, strict=True)
                self.button_click('remove', table)
            else:
                self.facet_button_click('remove')
            if fields:
                self.fill_fields(fields)
            self.dialog_button_click('ok')
            self.wait_for_request(n=2)
            self.wait()

    def navigate_to_entity(self, entity, facet=None):
        """
        Navigate to given entity e.g., user
        """
        self.driver.get(self.get_url(entity, facet))
        self.wait_for_request(n=3, d=0.4)

    def get_url(self, entity, facet=None):
        """
        Create entity url
        """
        url = [self.get_base_url(), '#', 'e', entity]
        if facet:
            url.append(facet)
        return '/'.join(url)

    def get_base_url(self):
        """
        Get FreeIPA Web UI url
        """
        host = self.config.get('ipa_server')
        if not host:
            self.skip('FreeIPA server hostname not configured')
        return 'https://%s/ipa/ui' % host

    def get_facet(self):
        """
        Get currently displayed facet
        """
        facet = self.find('.active-facet', By.CSS_SELECTOR)
        assert facet is not None, "Current facet not found"
        return facet

    def get_facet_info(self, facet=None):
        """
        Get information of currently displayed facet
        """
        info = {}

        # get facet
        if facet is None:
            facet = self.get_facet()
        info["element"] = facet

        # get facet name and entity
        info["name"] = facet.get_attribute('data-name')
        info["entity"] = facet.get_attribute('data-entity')

        # get facet title
        el = self.find(".facet-header h3 *:first-child", By.CSS_SELECTOR, facet)
        if el:
            info["title"] = el.text

        # get facet pkey
        el = self.find(".facet-header h3 span.facet-pkey", By.CSS_SELECTOR, facet)
        if el:
            info["pkey"] = el.text

        return info

    def navigate_to_record(self, pkey, parent=None, table_name=None, entity=None, facet='search'):
        """
        Clicks on record with given pkey in search table and thus cause
        navigation to the record.
        """
        if entity:
            self.navigate_to_entity(entity, facet)

        if not parent:
            parent = self.get_facet()

        s = self.get_table_selector(table_name)
        s += " tbody"
        table = self.find(s, By.CSS_SELECTOR, parent, strict=True)
        link = self.find(pkey, By.LINK_TEXT, table, strict=True)
        link.click()
        self.wait_for_request()

    def has_record(self, pkey, parent=None, table_name=None):
        """
        Check if table contains specific record.
        """
        if not parent:
            parent = self.get_form()

        s = self.get_table_selector(table_name)
        s += " tbody td input[value='%s']" % pkey
        checkbox = self.find(s, By.CSS_SELECTOR, parent)
        return checkbox is not None

    def get_table_selector(self, name=None):
        """
        Construct table selector
        """
        s = "table"
        if name:
            s += "[name='%s']" % name
        s += '.table'
        return s

    def get_form(self):
        """
        Get last dialog or visible facet
        """
        form = self.get_dialog()
        if not form:
            form = self.get_facet()
        return form

    def get_dialogs(self, strict=False, name=None):
        """
        Get all dialogs in DOM
        """
        s = '.modal-dialog'
        if name:
            s += "[data-name='%s']" % name
        dialogs = self.find(s, By.CSS_SELECTOR, many=True)
        if strict:
            assert dialogs, "No dialogs found"
        return dialogs

    def get_dialog(self, strict=False, name=None):
        """
        Get last opened dialog
        """
        dialogs = self.get_dialogs(strict, name)
        dialog = None
        if len(dialogs):
            dialog = dialogs[-1]
        return dialog

    def get_last_error_dialog(self, dialog_name='error_dialog'):
        """
        Get last opened error dialog or None.
        """
        s = ".modal-dialog[data-name='%s']" % dialog_name
        dialogs = self.find(s, By.CSS_SELECTOR, many=True)
        dialog = None
        if dialogs:
            dialog = dialogs[-1]
        return dialog

    def get_undo_buttons(self, field, parent):
        """
        Get field undo button
        """
        if not parent:
            parent = self.get_form()
        s = ".controls div[name='%s'] .btn.undo" % (field)
        undos = self.find(s, By.CSS_SELECTOR, parent, strict=True, many=True)
        return undos

    def get_rows(self, parent=None, name=None):
        """
        Return all rows of search table.
        """
        if not parent:
            parent = self.get_form()

        # select table rows
        s = self.get_table_selector(name)
        s += ' tbody tr'
        rows = self.find(s, By.CSS_SELECTOR, parent, many=True)
        return rows

    def get_row(self, pkey, parent=None, name=None):
        """
        Get row element of search table with given pkey. None if not found.
        """
        rows = self.get_rows(parent, name)
        s = "input[value='%s']" % pkey
        for row in rows:
            has = self.find(s, By.CSS_SELECTOR, row)
            if has:
                return row
        return None

    def assert_no_dialog(self):
        """
        Assert that no dialog is opened
        """
        dialogs = self.get_dialogs()
        assert not dialogs, 'Invalid state: dialog opened'

    def assert_dialog(self, name=None):
        """
        Assert that one dialog is opened or a dialog with given name
        """
        dialogs = self.get_dialogs(name)
        assert len(dialogs) == 1, 'No or more than one dialog opened'

    def assert_no_error_dialog(self):
        """
        Assert that no error dialog is opened
        """
        dialog = self.get_last_error_dialog()
        ok = dialog is None
        if not ok:
            msg = self.find('p', By.CSS_SELECTOR, dialog).text
            assert ok, 'Unexpected error: %s' % msg

    def assert_row_count(self, expected, current):
        """
        Assert that row counts match
        """
        assert expected == current, "Rows don't match. Expected: %d, Got: %d" % (expected, current)

    def facet_button_click(self, name):
        """
        Click on facet button with given name
        """
        facet = self.get_facet()
        s = ".facet-controls button[name=%s]" % name
        self._button_click(s, facet, name)

    def dialog_button_click(self, name, dialog=None):
        """
        Click on dialog button with given name

        Chooses last dialog if none is supplied
        """
        if not dialog:
            dialog = self.get_dialog(strict=True)

        s = ".rcue-dialog-buttons button[name='%s']" % name
        self._button_click(s, dialog, name)

    def action_button_click(self, name, parent):
        """
        Click on .action-button
        """
        if not parent:
            parent = self.get_form()

        s = "a[name='%s'].action-button" % name
        self._button_click(s, parent, name)

    def _button_click(self, selector, parent, name=''):
        """
        Private function to click on given button name
        """
        btn = self.find(selector, By.CSS_SELECTOR, parent, strict=True)
        ActionChains(self.driver).move_to_element(btn).perform()
        disabled = btn.get_attribute("disabled")
        assert btn.is_displayed(), 'Button is not displayed: %s' % name
        assert not disabled, 'Invalid button state: disabled. Button: %s' % name
        btn.click()
        self.wait_for_request()

    def fill_fields(self, fields, parent=None, undo=False):
        """
        Fill dialog or facet inputs with give data.

        Expected format:
        [
            ('widget_type', 'key', value'),
            ('widget_type', 'key2', value2'),
        ]
        """

        if not parent:
            parent = self.get_form()

        for field in fields:
            widget_type = field[0]
            key = field[1]
            val = field[2]

            if undo and not hasattr(key, '__call__'):
                self.assert_undo_button(key, False, parent)

            if widget_type == 'textbox':
                self.fill_textbox(key, val, parent)
            elif widget_type == 'textarea':
                self.fill_textarea(key, val, parent)
            elif widget_type == 'password':
                self.fill_password(key, val, parent)
            elif widget_type == 'radio':
                self.check_option(key, val, parent)
            elif widget_type == 'checkbox':
                self.check_option(key, val, parent=parent)
            elif widget_type == 'selectbox':
                self.select('select[name=%s]' % key, val, parent)
            elif widget_type == 'combobox':
                self.select_combobox(key, val, parent)
            elif widget_type == 'add_table_record':
                self.add_table_record(key, val, parent)
            elif widget_type == 'add_table_association':
                self.add_table_associations(key, val, parent)
            elif widget_type == 'multivalued':
                self.fill_multivalued(key, val, parent)
            elif widget_type == 'table':
                self.select_record(val, parent, key)
            # this meta field specifies a function, to extend functionality of
            # field checking
            elif widget_type == 'callback':
                if hasattr(key, '__call__'):
                    key(val)
            self.wait()
            if undo and not hasattr(key, '__call__'):
                self.assert_undo_button(key, True, parent)

    def fill_text(self, selector, value, parent=None):
        """
        Clear and enter text into input defined by selector.
        Use for non-standard fields.
        """
        if not parent:
            parent = self.get_form()
        tb = self.find(selector, By.CSS_SELECTOR, parent, strict=True)
        try:
            tb.clear()
            tb.send_keys(value)
        except InvalidElementStateException as e:
            msg = "Invalid Element State, el: %s, value: %s, error: %s" % (selector, value, e)
            assert False, msg

    def fill_input(self, name, value, input_type="text", parent=None):
        """
        Type into input element specified by name and type.
        """
        s = "div[name='%s'] input[type='%s'][name='%s']" % (name, input_type, name)
        self.fill_text(s, value, parent)

    def fill_textarea(self, name, value, parent=None):
        """
        Clear and fill textarea.
        """
        s = "textarea[name='%s']" % (name)
        self.fill_text(s, value, parent)

    def fill_textbox(self, name, value, parent=None):
        """
        Clear and fill textbox.
        """
        self.fill_input(name, value, "text", parent)

    def fill_password(self, name, value, parent=None):
        """
        Clear and fill input[type=password]
        """
        self.fill_input(name, value, "password", parent)

    def add_multivalued(self, name, value, parent=None):
        """
        Add new value to multivalued textbox
        """
        if not parent:
            parent = self.get_form()
        s = "div[name='%s'].multivalued-widget" % name
        w = self.find(s, By.CSS_SELECTOR, parent, strict=True)
        add_btn = self.find("button[name=add]", By.CSS_SELECTOR, w, strict=True)
        add_btn.click()
        s = "div[name=value] input"
        inputs = self.find(s, By.CSS_SELECTOR, w, many=True)
        last = inputs[-1]
        last.send_keys(value)

    def del_multivalued(self, name, value, parent=None):
        """
        Mark value in multivalued textbox as deleted.
        """
        if not parent:
            parent = self.get_form()
        s = "div[name='%s'].multivalued-widget" % name
        w = self.find(s, By.CSS_SELECTOR, parent, strict=True)
        s = "div[name=value] input"
        inputs = self.find(s, By.CSS_SELECTOR, w, many=True)
        clicked = False
        for i in inputs:
            val = i.get_attribute('value')
            n = i.get_attribute('name')
            if val == value:
                s = "input[name='%s'] ~ .input-group-btn button[name=remove]" % n
                link = self.find(s, By.CSS_SELECTOR, w, strict=True)
                link.click()
                self.wait()
                clicked = True

        assert clicked, 'Value was not removed: %s' % value

    def fill_multivalued(self, name, instructions, parent=None):
        """
        Add or delete a value from multivalued field
        """
        for instruction in instructions:
            t = instruction[0]
            value = instruction[1]
            if t == 'add':
                self.add_multivalued(name, value, parent)
            else:
                self.del_multivalued(name, value, parent)

    def get_dialog_info(self):
        """
        Get last open dialog info: name, text if any.
        Returns None if no dialog is open.
        """
        dialog = self.get_dialog()

        info = None
        if dialog:
            body = self.find('.modal-body', By.CSS_SELECTOR, dialog, strict=True)
            info = {
                'name': dialog.get_attribute('data-name'),
                'text': body.text,
            }
        return info

    def select_record(self, pkey, parent=None, table_name=None):
        """
        Select record with given pkey in search table.
        """
        if not parent:
            parent = self.get_form()

        s = self.get_table_selector(table_name)
        input_s = s + " tbody td input[value='%s']" % pkey
        checkbox = self.find(input_s, By.CSS_SELECTOR, parent, strict=True)
        checkbox_id = checkbox.get_attribute('id')
        label_s = s + " tbody td label[for='%s']" % checkbox_id
        label = self.find(label_s, By.CSS_SELECTOR, parent, strict=True)
        try:
            ActionChains(self.driver).move_to_element(label).click().perform()
        except WebDriverException as e:
            assert False, 'Can\'t click on checkbox label: %s \n%s' % (s, e)
        self.wait()
        assert checkbox.is_selected(), 'Record was not checked: %s' % input_s
        self.wait()

    def mod_record(self, entity, data, facet='details', facet_btn='save'):
        """
        Mod record

        Assumes that it is already on details page.
        """
        self.assert_facet(entity, facet)
        self.assert_facet_button_enabled(facet_btn, enabled=False)
        self.fill_fields(data['mod'], undo=True)
        self.assert_facet_button_enabled(facet_btn)
        self.facet_button_click(facet_btn)
        self.wait_for_request()
        self.wait_for_request()
        self.assert_facet_button_enabled(facet_btn, enabled=False)

    def action_list_action(self, name, confirm=True, confirm_btn="ok"):
        """
        Execute action list action
        """
        cont = self.find(".active-facet .facet-actions", By.CSS_SELECTOR, strict=True)
        expand = self.find(".dropdown-toggle", By.CSS_SELECTOR, cont, strict=True)
        expand.click()
        action_link = self.find("li[data-name=%s] a" % name, By.CSS_SELECTOR, cont, strict=True)
        action_link.click()
        if confirm:
            self.wait(0.5)  # wait for dialog
            self.dialog_button_click(confirm_btn)
        self.wait()
