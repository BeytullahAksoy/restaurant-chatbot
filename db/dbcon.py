from rethinkdb import RethinkDB

r = RethinkDB()
r.connect("localhost", 28015).repl()


def insert_customer(customer_name, customer_address, customer_phone_number, customer_email):
    r.table("customers").insert([
        {"name": customer_name, "address": customer_address,
         "phone_number": customer_phone_number, "email": customer_email
         }
    ]).run()


def update_customer(customer_name, customer_address, customer_phone_number, customer_email):
    r.table("customers").filter(r.row["name"] == customer_name).update(
        {"name": customer_name, "address": customer_address,
         "phone_number": customer_phone_number, "email": customer_email
         }).run()


def delete_customer(customer_name):
    r.table("customers").filter(r.row["name"] == customer_name).delete().run()


def query_customer_by_name(customer_name):
    return r.table("customers").filter(r.row["name"] == customer_name).run()


def query_customer_by_email(customer_email):
    return r.table("customers").filter(r.row["email"] == customer_email).run()


def query_customer_by_phone_number(customer_phone_number):
    return r.table("customers").filter(r.row["phone_number"] == customer_phone_number).run()


def insert_order(id, foods, customer_name, order_status):
    r.table("orders").insert([
        {"id": id, "foods": foods,
         "customer_name": customer_name, "order_status": order_status
         }
    ]).run()


def delete_order(id):
    r.table("orders").filter(r.row["id"] == id).delete().run()


def update_order_status(id, order_status):
    r.table("orders").filter(r.row["id"] == id).update({"order_status": order_status}).run()


def get_customer_by_order_id(id):
    customer_name = r.table("orders").get(id)["customer_name"].run()
    return r.table("customers").filter(r.row["name"] == customer_name).run()


def get_unprepared_orders():
    return r.table("orders").filter(r.row["order_status"] == "preparing").run()


