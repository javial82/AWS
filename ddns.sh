#!/bin/bash

recordset=$1
hostedzoneid=$2

if [ -z ${recordset+x} ] || [ -z ${hostedzoneid} ]
then
  echo "Usage: ./ddns.sh foo.bar.com F3454GSGFW42DF"
  echo -e '\t$1 the dns name to update, ex: foo.bar.com'
  echo -e '\t$2 the hosted zone id in your R53 service, ex: F3454GSGFW42DF'


  exit 1
fi

localip=$(curl https://ipinfo.io/ip 2>/dev/null)
remoteip=$(dig +short $recordset)

if [ $localip == $remoteip ]
then
  logger "ddns.sh: Nothing to do."
else
  cat << EOF > /tmp/ddns.json
{
  "Comment": "update home ip",
  "Changes": [
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": $recordset",
        "Type": "A",
        "TTL": 300,
        "ResourceRecords": [
          {
            "Value": "$localip"
          }
        ]
      }
    }
  ]
}
EOF
  aws route53 change-resource-record-sets --hosted-zone-id $hostedzoneid --change-batch file:///tmp/ddns.json
  logger "ddns.sh: IP changed to $localip."
  rm -rf /tmp/ddns.json
fi
