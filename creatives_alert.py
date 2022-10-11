import pandas as pd
import numpy as np
import requests
import datetime

# get data from MCP Slack Alert spreadsheet

# get token
gentoken_url = "https://api.moloco.cloud/cm/v1/auth/tokens"

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}
payload_token={"email": "youremail", "password": "yourpassword","workplace_id":"BBGame"}


try:
 response = requests.post(gentoken_url, headers=headers,json=payload_token)
 token=response.json()['token']
except: 
  print(response.text)


# pull the CreativeReview data
CreativeReviews_url = "https://api.moloco.cloud/cm/v1/creative-reviews"

params={
    'ad_account_id':"D4YjyUuKoZi0OHP3",
    'review_states':['BLOCKED']

}
headers = {
    "Accept": "application/json",
    "Authorization": "Bearer "+token
}
try: 
  response = requests.get(CreativeReviews_url, headers=headers, params=params)
  res_dict=response.json()['creative_reviews']
except:
  print(response.text)

# the block exchange sometimes is a list which include many items, but only select first for the simple's sake
cr_group=[ i['creative_groups_using_creative'][0]['title'] for i in res_dict]
cr_title=[ i['creative']['original_filename'] for i in res_dict]
block_exchange=[list(i['reviews'])[0] for i in res_dict]
block_time_date=[ datetime.datetime.strptime(list(i['reviews'].values())[0]['action_history'][0]['created_at'].rsplit('T')[0],"%Y-%m-%d").date() for i in res_dict]


if len(block_exchange)==len(cr_group)==len(cr_title)==len(block_time_date):
  pass
else:
  print("the items length are not queal")
today=datetime.date.today()
# today=date.today().strftime('%Y-%m-%d')
yesterday=datetime.date.today()-datetime.timedelta(days=1)


cr_review_list=list(zip(cr_group,cr_title,block_exchange,block_time_date))
cr_alert_set_list=[]
for i in cr_review_list:
  if datetime.datetime(2022,10,10).date()<i[3]<=today:
    cr_alert_set_list.append(i) 
  else:
    continue

unique_exchange_set=set([ i[2] for i in cr_alert_set_list])
exchange_string=','.join(unique_exchange_set)
cr_title_string='\n '.join([i[1] for i in cr_alert_set_list])
cr_group_string='\n '.join([i[0] for i in cr_alert_set_list])

# build slack blockkit
webhook_url= "https://hooks.slack.com/services/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"
slack_alerts_blockkit={
    "blocks": [
      {
        "type": "header",
        "text": {
          "type": "plain_text",
          "text": "Creatives Review Status Disapproved Alert"
        }
      },
      {
        "type": "divider"
      },
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": f"*Exchange*:\t {exchange_string} "
        }
      },
      {
			"type": "section",
			"fields": [
				{
					"type": "mrkdwn",
					"text": f"*Creative Title:*\n {cr_title_string}"
				},
				{
					"type": "mrkdwn",
					"text": f"*Creative Group:*\n {cr_group_string}"
				},
        			]
		},
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": f"*Disapproved Date*:\t {cr_alert_set_list[0][3]}"
        }
      }
    ]
}


# post to incoming webhooks
slack_webhook_headers={"contentType": "application/json"}
try:
  response=requests.post(webhook_url,headers=slack_webhook_headers,json=slack_alerts_blockkit)
  print(response.text)
except:
  print("error")
  
  
# if error requests.exceptions.SSLError: HTTPSConnectionPool(host='api.moloco.cloud', port=443):
# Max retries exceeded with url: /cm/v1/auth/tokens (Caused by SSLError(SSLEOFError(8, 'EOF occurred in violation of protocol (_ssl.c:1129)')))
# install pip install urllib3==1.25.11