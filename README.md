## Moch Dira Monitoring Script

This Python script is designed to automate the process of logging into the website of the Israeli Ministry of Construction and Housing (https://www.dira.moch.gov.il/) to check the status of lottery applications. The script logs into the website, retrieves the list of lotteries a user is participating in, checks if there have been any changes in the order, and saves the history of orders. It also sends notifications to a specified Telegram chat whenever there is a change in order.

### Features
- Automated login to the website.
- Retrieving the list of lotteries a user is participating in.
- Monitoring for changes in the order of the lottery.
- Saving the history of orders.
- Notifying a Telegram chat when a change in order occurs.
- Scheduling regular checks for changes in order.
- Scheduling a weekly update on the status of the lotteries.

### Usage

Firstly, you need to fill in your personal information in the script:

- Replace ID_NUMBER with your ID number.
- Replace PARTNER_ID_NUMBER with your partner's ID number.
- Replace PASSWORD with your password.

For Telegram notifications, you need to provide:

- Replace bot_token with your Telegram bot token.
- Replace chat_id with your Telegram chat id.
- To run the script, simply execute it with a Python interpreter. It will automatically log into the website, check the status of the lotteries, and begin monitoring for changes. It will continue to check for changes every 6 hours and send an update to the specified Telegram chat every Sunday at 8:00.

### Requirements
- Python 3 (Checked on 3.11)
- (optional) A Telegram bot and chat for receiving notifications.

### Notes
The script is designed to be run continuously in order for the monitoring and notifications to work.
Please ensure that the computer or server running the script has a stable internet connection.
You should replace the placeholders in the script with your own personal information and Telegram bot information before running it.
This script is for educational purposes only. Please use responsibly and ensure that it complies with the website's terms of service.
