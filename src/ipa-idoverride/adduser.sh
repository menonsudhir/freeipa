#!/bin/bash

if [[ x"$1" == x"" ]]; then
    echo "Server name required"
    exit 1
else
    server=$1
fi

ORGIFS=$IFS
IFS="." read -r -a domainarray <<< $server
IFS=$ORGIFS

dcstr=""
domain=""
for element in "${domainarray[@]:1}"
do
    if [[ x"$dcstr" == x"" ]]; then
        dcstr="dc=$element"
    else
        dcstr="$dcstr,dc=$element"
    fi

    if [[ x"$domain" == x"" ]]; then
        domain=$element
    else
        domain="$domain.$element"
    fi
done

updomain=`echo $domain |  tr '[:lower:]' '[:upper:]'`
echo Secret123 | kinit "Administrator@$updomain"

for i in {1..20}; do net -k -S ${server} ads user add idviewuser$i; done

cat > /tmp/template.ldif <<EOF
dn: cn=NAME,cn=users,$dcstr
changetype: modify
add: msSFU30Name
msSFU30Name: NAME
-
add: msSFU30NisDomain
msSFU30NisDomain: $dcstr
-
EOF

for i in {1..20}; do
    sed -e s/NAME/test${i}/g -e s/UID/${uid}/g /tmp/template.ldif > /tmp/$i.ldif
    ldapmodify -Y gssapi -H ldap://${server} -f /tmp/$i.ldif
    rm -f /tmp/$i.ldif
    let uid=$uid+1
done

rm -f /tmp/template.ldif
