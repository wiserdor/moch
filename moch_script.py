
import requests
import json
import schedule
import time
import datetime

# Replace with your ID number
id_number = "ID_NUMBER"
# Replace with your partner's ID number (Wife, Husband, etc.)
partner_id_number = "PARTNER_ID_NUMBER"

# Define the URLs
login_url = "https://www.dira.moch.gov.il/api/users/Login"
data_url = f"https://www.dira.moch.gov.il/api/InvokerAuth?method=LotteryResult%2FMyLotteryListQuery&param=%3FFirstApplicantIdentityNumber%3D{id_number}%26SecondApplicantIdentityNumber%3D{partner_id_number}%26LoginId%3D{id_number}%26"

# Define the login data
login_data = {
    "identity": id_number,
    "password": "PASSWORD"  # Replace with your password
}

# Telegram Data
# Replace with your bot token
bot_token = None
chat_id = None  # Replace with your chat id

# Initialize the previous data
# if there is a history file, load it
try:
    with open("history.json", "r") as f:
        history = json.load(f)
# otherwise, create a new one
except FileNotFoundError:
    history = {}


def prettify_date(date):
    try:
        return date.split("T")[0]
    except:
        return date


def send_telegram_message(message):
    if bot_token is None or chat_id is None:
        return
    # if message is longer than 4096 characters, split it into multiple messages
    if len(message) > 4096:
        for i in range(0, len(message), 4096):
            send_telegram_message(message[i:i+4096])
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=data)
    return response.json()


def check_lottery():
    global previous_data
    print("Checking lottery...")
    # Start a session
    session = requests.Session()

    # Login
    response = session.post(login_url, data=login_data)

    # Check if the login was successful
    if response.status_code == 200:
        session.headers.update(
            {"Authorization": f'Basic {response.headers["Sessionid"]}'})
        # Get the JSON data
        response = session.get(data_url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON data
            data = json.loads(response.text)
            my_lottery_list = [
                {
                    "id": d["LotteryNumber"],
                    "city": d["CityDescription"],
                    "order": d["ApartmentSelectOrder"],
                    "resident_order":d["ApartmentSelectOrderLocal"],
                    "total_apartments":d["LotteryApartmentsCount"],
                    "lottery_date":d["LotteryDate"],
                } for d in data["MyLotteryList"]]

            # Compare the new data with the history
            timestamp = time.time()
            for item in my_lottery_list:
                history_item = {
                    "timestamp": timestamp,
                    "order": item["order"],
                    "resident_order": item["resident_order"],
                    "city": item["city"],
                    "total_apartments": item["total_apartments"],
                    "lottery_date": item["lottery_date"]
                }

                if item["id"] not in history:
                    history[item["id"]] = []
                    history[item["id"]].append(history_item)
                else:
                    last_item = history[item["id"]][-1]
                    if last_item["order"] != item["order"] or last_item["resident_order"] != item["resident_order"]:
                        print(f"Order changed for lottery id {item['id']}.")
                        print(f"Previous data: {last_item}")
                        print(f"Current data: {item}")
                        history[item["id"]].append(history_item)

                        # prettify lottery date for telegram:

                        lottery_date = prettify_date(item["lottery_date"])

                        send_telegram_message(
                            f'Order changed for lottery id {item["id"]}\nIn {item["city"]} made on {lottery_date}.\nThe order changed from {last_item["order"]} to {item["order"]}.\nresident order changed from {last_item["resident_order"]} to {item["resident_order"]}.')

            # Save the history
            with open("history.json", "w", encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=4)
        else:
            print(f"Failed to get data, status code: {response.status_code}")
    else:
        print(f"Login failed, status code: {response.status_code}")


def get_list_of_lotteries_by_order():
    global history

    # Get the list of lotteries
    lotteries = []
    for lottery_id in history:
        # if lottery order is less than 0, skip it
        if history[lottery_id][-1]["order"] < 0:
            continue

        last_item = history[lottery_id][-1]
        lotteries.append(
            {
                "id": lottery_id,
                "order": last_item["order"],
                "resident_order": last_item["resident_order"],
                "city": last_item["city"],
                "total_apartments": last_item["total_apartments"],
                "lottery_date": last_item["lottery_date"],
                "timestamp": last_item["timestamp"] if "timestamp" in last_item else ""
            }
        )

    # Sort the list by order
    lotteries.sort(key=lambda x: x["order"])

    # create a string with the list of lotteries
    lotteries_string = ""

    for i, lottery in enumerate(lotteries[:10]):
        last_updated = datetime.datetime.fromtimestamp(
            lottery["timestamp"]).strftime('%Y-%m-%d')
        # prettify message for telegram:
        lotteries_string += f"{i+1}.\nLottery id: {lottery['id']}\nCity: {lottery['city']}\nOrder: {lottery['order']}\nResident Order: {lottery['resident_order']}\nTotal Apartments: {lottery['total_apartments']}\nDate: {prettify_date(lottery['lottery_date'])}\nlast updated: {last_updated}\n\n"

    return lotteries_string


# send_telegram_message(json.dumps(history, ensure_ascii=False, indent=4))
send_telegram_message(get_list_of_lotteries_by_order())
check_lottery()

# Schedule the function to run every X minutes
schedule.every(12).hours.do(check_lottery)

# Schedule the function to run every day at 8:00
schedule.every().sunday.at("08:00").do(
    lambda: send_telegram_message(get_list_of_lotteries_by_order()))

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)
