export BRANCH=$1
export REVISION=`git rev-parse $BRANCH`
export APP_ID=22960038
export APP_KEY=c9a9546e2530ea5040e45db4b7e373545ea5462416d6872
export CHANGELOG=`git log --oneline -1 $BRANCH`

curl -X POST "https://api.newrelic.com/v2/applications/${APP_ID}/deployments.json" \
     -H "X-Api-Key:${APP_KEY}" -i \
     -H "Content-Type: application/json" \
     -d \
"{
  \"deployment\": {
   \"revision\": \"${REVISION}\",
    \"changelog\": \"${CHANGELOG}\",
    \"description\": \"briefy.leica deployed from ${BRANCH} branch or tag\",
    \"user\": \"developer@briefy.co\"
  }
}"
