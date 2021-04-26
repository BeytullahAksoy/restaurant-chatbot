import csv

import Levenshtein as lev
import datetime
import re
from datetime import datetime
from typing import Dict, Any, List
from typing import Text
from datetime import datetime
from datetime import timedelta
from typing import Text, Union


import sys

from db.dbcon import *

sys.path.insert(0, 'db/dbcon')





import dateparser as dp
import re

from turkish.deasciifier import Deasciifier
from rasa_sdk import Tracker
from rasa_sdk.types import DomainDict
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction, Action, FormAction


def turkify(text: Text) -> Union[Text, None]:
    if text:
        deasciifier = Deasciifier(text)
        return deasciifier.convert_to_turkish()
    else:

        return None


def parse_date_tr(date: Text) -> Union[datetime, None]:
    """
    Wrapper for dateparser.parse. Parses given Turkish date.
    """
    next_week = ("haftaya", "gelecek hafta", "sonraki hafta")
    days = ("pazartesi", "salı", "çarşamba", "perşembe", "cuma", "cumartesi", "pazar")
    remaining_days = days[datetime.today().weekday() + 1:]
    if date := turkify(date.casefold()):
        days_to_add = 0
        for day in remaining_days:
            if bool(re.match(r"\b({0})\b".format(day), date)):
                days_to_add += 7
                break
        for prefix in next_week:
            if prefix in date:
                days_to_add += 7
                date = date.replace(prefix, "")
                break
        if parsed_date := dp.parse(date, languages=["tr"]):
            parsed_date += timedelta(days=days_to_add)

            return parsed_date
    return False





basket_names = []
basket_counts = []
orders = [[]]

reader = csv.reader(
    open("menu.csv"), delimiter=";")


class ValidateReservationForm(FormValidationAction):

    def isValidTime(time: str) -> bool:
        regex = r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
        return bool(re.match(regex, time))

    def name(self) -> Text:
        return "validate_reservation_form"

    def validate_person_count(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        if int(slot_value).isnumeric() and len(slot_value) > 0:
            return {"person_count": float(slot_value)}
        else:
            dispatcher.utter_message(template="utter_wrong_person_count")
            return {"person_count": None}

    def validate_person_name(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if slot_value.replace(" ", "").isalpha() and len(slot_value.replace(" ", "")) >= 3:
            global name
            name = slot_value
            return {"person_name": slot_value}
        else:
            dispatcher.utter_message(template="utter_wrong_person_name")
            return {"person_name": None}

    def validate_person_phone_number(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if slot_value.isnumeric() and int(slot_value) > 0 and (len(slot_value) == 10 or len(slot_value) == 11):
            return {"person_phone_number": slot_value}
        else:
            dispatcher.utter_message(template="utter_wrong_person_phone_number")
            return {"person_phone_number": None}

    def validate_reservation_hour(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        booleanCheck = self.isValidTime(slot_value)  ##boolean value fron m function that check if slot value is type 24 hour
        if booleanCheck:
            return {"reservation_hour": slot_value}
        else:
            dispatcher.utter_message(template="utter_wrong_reservation_hour")
            return {"reservation_hour": None}

    def validate_reservation_date(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        try:
            d = datetime.strptime(slot_value, "%Y-%m-%d").date()
            now = datetime.now().date()
            if (d - now).days < 14 and (d - now).days >= 0:
                return {"reservation_date": slot_value}
        except:
            pass

        try:
            if parse_date_tr(slot_value):
                return {"reservation_date": parse_date_tr(slot_value).date().strftime("%Y/%m/%d")}
            else:
                dispatcher.utter_message(template="utter_wrong_reservation_date")
                return {"reservation_date": None}
        except:
            return {"reservation_date": None}


def match_food(s: str) -> Union[str, List[str]]:
    food_array = []
    Str1 = s
    reader = csv.reader(
        open("menu.csv"), delimiter=";")
    for row in reader:

        Str2 = row[0]
        Ratio = lev.ratio(Str1.lower(), Str2.lower())
        print(Ratio)
        if (Ratio > 0.9):
            print(row[0])
            return row[0]
        elif (Ratio > 0.4):
            food_array.append(row[0])

    return food_array


foods = []
prices = []
descriptions = []
categories = []
orders = [[]]
currentUser = []
name = ""
email = ""
phone = ""
address=""

class ValidateOrderForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_order_form"

    for row in reader:
        categories.append(row[3])
        descriptions.append(row[2])
        prices.append(row[1])
        foods.append(row[0])
    categories.pop(0)
    descriptions.pop(0)
    prices.pop(0)
    foods.pop(0)

    def validate_food(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        """


        """
        match = match_food(tracker.latest_message["text"])
        print(f"{match}")
        if (slot_value == "sorgu"):
            return {"food": [], "food_count": [], "situation_order": None}
        if (slot_value == "iptal" or slot_value == "sil" or slot_value == "çıkar"):
            print("food to cancel")
            if len(basket_names) == 0:
                dispatcher.utter_message("Sepetinizde ürün bulunmamaktadır.")
                return {"food": None}
            return {"food": [], "food_count": [], "cancel_food": None}

        if isinstance(match, str):

            basket_names.append(match)
            print(len(basket_names))

            return {"food": [], "food_count": None}

        elif tracker.latest_message["text"] in categories:
            dispatcher.utter_message(tracker.latest_message["text"] + " kategorisindeki ürünler")
            a = 0
            for i in categories:
                if tracker.latest_message["text"] == categories[a]:
                    dispatcher.utter_message(foods[a])
                    a = a + 1
            return {"food": None}



        elif (len(match) > 0):
            print("seçeneklerde")
            dispatcher.utter_message("Aramanıza uygun şunlar bulundu")

            for i in match:
                dispatcher.utter_message(i)

            return {"food": None}
        elif (tracker.latest_message["text"] == "bitir"):

            currentUser.append(basket_names)
            currentUser.append(basket_counts)
            print(currentUser)
            return {"food": basket_names,
                    "food_count": basket_counts,
                    "cancel_food": 1,
                    "situation_order": 1}



        else:
            print("bulunamadı")
            dispatcher.utter_message(template="utter_wrong_food")

            return {"food": None}

    def validate_food_count(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if slot_value.isnumeric():
            basket_counts.append(slot_value)
            if len(basket_names) > 0:
                dispatcher.utter_message("Sepetinizdeki ürünler:")
                i = 0
                while i < len(basket_names):
                    dispatcher.utter_message(basket_names[i] + " " + basket_counts[i] + " adet")

                    i = i + 1
            return {"food_count": None,
                    "food": None}

        else:

            dispatcher.utter_message(template="utter_wrong_food_count")

            return {"food_count": None,
                    "food": None}

    def validate_cancel_food(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        print("cancel food geldi")
        print(len(basket_names))

        match = match_food(tracker.latest_message["text"])
        print("the match : " + str(match))
        print(f"{match}")
        a = 0
        if match and match in basket_names:
            dispatcher.utter_message(match + " sepetinizden silindi.")
            i = basket_names.index(match)
            print("before")
            print("counts :")
            print(basket_counts)
            print("foods: ")
            print(basket_names)
            basket_names.remove(match)
            del basket_counts[i]
            print("after: ")
            print("i: " + str(i))
            print("counts :")
            print(basket_counts)
            print("foods: ")
            print(basket_names)
            print("a deleted " + str(a))

            return {"food": None}
        elif match and not str(match) in basket_names:
            print("not in")
            dispatcher.utter_message("Bu ürün sepetinizde bulunmamaktadır")
            return {"food": None}
        else:
            print("else")
            dispatcher.utter_message("Hatalı yemek adı girdiniz.Lütfen yemek adını doğru giriniz.")
            return {"cancel_food": None}

    def validate_person_name(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if slot_value.replace(" ", "").isalpha() and len(slot_value.replace(" ", "")) >= 3:
            currentUser.append(slot_value)
            return {"person_name": slot_value}
        else:
            dispatcher.utter_message(template="utter_wrong_person_name")
            return {"person_name": None}

    def validate_situation_order(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        for i in orders:
            if slot_value in i:
                print(i[5])
                return {"food": None}

    def validate_person_address(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if len(slot_value) > 1:
            currentUser.append(slot_value)
            return {"person_address": slot_value}
        else:
            dispatcher.utter_message(template="utter_wrong_person_address")
            return {"person_address": None}

    def validate_person_email(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if len(slot_value) > 1:
            global email
            email=slot_value
            currentUser.append(slot_value)
            return {"person_email": slot_value}
        else:
            dispatcher.utter_message(template="utter_wrong_person_email")
            return {"person_email": None}

    def validate_person_phone_number(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if slot_value.isnumeric() and int(slot_value) > 0 and (len(slot_value) == 10 or len(slot_value) == 11):
            global name
            global email
            global address
            print("g name :"+name)
            print("g mail :"+email)
            print("g address:"+address)
            currentUser.append(slot_value)
            currentUser.append("preparing")
            orders.append(currentUser)
            print(currentUser)
            print("value 0 :")
            print(currentUser[0])
            print("value 1 :")
            print(currentUser[1])
            insert_customer(name, address, slot_value,
                                 email)
            x = zip(basket_names, basket_counts)

            insert_order(x, name, "preparing")
            print("unprepared orders:")
            print(get_unprepared_orders())
            print("tracker name : " + name)
            return {"person_phone_number": slot_value}


        else:
            dispatcher.utter_message(template="utter_wrong_person_phone_number")

            return {"person_phone_number": None}


class ListMenu(Action):

    def name(self) -> Text:
        return "list_menu"

    def run(self, dispatcher, tracker: Tracker, domain: "DomainDict") -> List[Dict[Text, Any]]:

        dispatcher.utter_message('Sipariş edebileceğiniz yemek kategorileri gösterilmektedir. ')
        # intilize a null list
        unique_list = []

        # traverse for all elements
        for x in categories:
            # check if exists in unique_list or not
            if x not in unique_list:
                unique_list.append(x)
        # print list

        for i in unique_list:
            dispatcher.utter_message(i)
            print("category:" + " " + i)
        dispatcher.utter_message(
            ' Sipariş etmek istediğiniz kategoriyi yazabilir ya da istediğiniz yemeğin adını doğrudan yazabilirsiniz. \n Sepetten ürün çıkarmak için "iptal" komutunu kullanın ')
        return []


class GreetUser(Action):

    def name(self) -> Text:
        return "greet_user"

    def run(self, dispatcher, tracker: Tracker, domain: "DomainDict") -> List[Dict[Text, Any]]:
        dispatcher.utter_message("Merhaba, restoranımıza hoşgeldiniz. \n Sipariş ya da rezervasyon verebilirsiniz.")

        return []


"""
class ReservationAction(Action):
    async def run(self, dispatcher, tracker: Tracker, domain: "DomainDict") -> List[Dict[Text, Any]]:

         TODO:
         Send the reservation info to the restaurant.

         food = tracker.get_slot("food")

         print(f"Reservation sent for {food}  for")

    def name(self) -> Text:
         return "reservation_action"
"""