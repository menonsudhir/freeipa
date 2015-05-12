#!/bin/sh -ex

# PURPOSE:
# After the commit in the local repo, rfc.sh is used to
# generate "Change Id" tag for gerrit purpose, rebase the
# changes against the master HEAD and upload the patch to
# gerrit.

#Usage: After local commit run ./rfc.sh

branch="master";

# On the first execution this function downloads a git hook
# from the below url and sets it up locally. This hooks is
# then used to generate the "Change Id" tag in the commit
# message. Gerrit identifes changes or patches based on this
# "Change Id" tag.


set_hooks_commit_msg()
{
    f=".git/hooks/commit-msg";
    u="https://code.engineering.redhat.com/gerrit/tools/hooks/commit-msg";

    if [ -x "$f" ]; then
        return;
    fi

    curl -o $f $u || wget --no-check-certificate -O $f $u;

    chmod +x .git/hooks/commit-msg;

    # Let the 'Change-Id: ' header get assigned on first run of rfc.sh
    GIT_EDITOR=true git commit --amend;
}


is_num()
{
    local num;

    num="$1";

    [ -z "$(echo $num | sed -e 's/[0-9]//g')" ]
}

# rebase the change against the master HEAD.
rebase_changes()
{
    git fetch origin;

    GIT_EDITOR=$0 git rebase -i origin/$branch;
}


editor_mode()
{
    if [ $(basename "$1") = "git-rebase-todo" ]; then
        sed 's/^pick /reword /g' "$1" > $1.new && mv $1.new $1;
        return;
    fi

    if [ $(basename "$1") = "COMMIT_EDITMSG" ]; then
        if grep -qi '^BUG: ' $1; then
            return;
        fi
        while true; do
            echo Commit: "\"$(head -n 1 $1)\""
            # echo -n "Enter Bug ID: "
            # read bug
            if [ -z "$bug" ]; then
                return;
            fi
            if ! is_num "$bug"; then
                echo "Invalid Bug ID ($bug)!!!";
                continue;
            fi

            sed "/^Change-Id:/{p; s/^.*$/BUG: $bug/;}" $1 > $1.new && \
                mv $1.new $1;
            return;
        done
    fi

    cat <<EOF
$0 - editor_mode called on unrecognized file $1 with content:
$(cat $1)
EOF
    return 1;
}


assert_diverge()
{
    git diff origin/$branch..HEAD | grep -q .;
}


main()
{
    set_hooks_commit_msg;

    if [ -e "$1" ]; then
        editor_mode "$@";
        return;
    fi

    rebase_changes;

    assert_diverge;

    bug=$(git show --format='%b' | grep -i '^BUG: ' | awk '{print $2}');

    if [ "$DRY_RUN" = 1 ]; then
        drier='echo -e Please use the following command to send your commits to review:\n\n'
    else
        drier=
    fi

    if [ -z "$bug" ]; then
        $drier git push origin HEAD:refs/for/$branch/rfc;
    else
        $drier git push origin HEAD:refs/for/$branch/bug-$bug;
    fi
}

main "$@"
