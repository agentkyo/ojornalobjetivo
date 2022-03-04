import requests
import email.message
import smtplib
import sqlite3
import json
from bs4 import BeautifulSoup
import re
from flask import Flask, render_template


class Database:
    @staticmethod
    def reset_bank():
        banco = sqlite3.connect("data.db")
        cursor = banco.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS locker (name text, value text)")
        cursor.execute("INSERT or REPLACE INTO locker VALUES('gpass', '')")
        cursor.execute("CREATE TABLE IF NOT EXISTS members (name text, email text)")
        banco.commit()

    @staticmethod
    def add_member(name: str, email: str):
        banco = sqlite3.connect("data.db")
        cursor = banco.cursor()
        cursor.execute(
            "INSERT or REPLACE INTO members VALUES('{}', '{}')".format(name, email)
        )
        banco.commit()

    @staticmethod
    def remove_member(email: str):
        banco = sqlite3.connect("data.db")
        cursor = banco.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS locker (name text, value text)")
        cursor.execute("INSERT or REPLACE INTO locker VALUES('gpass', '')")
        banco.commit()


class Newsletter:
    @staticmethod
    def update_uol() -> list:
        url = "https://www.uol.com.br/"

        r = requests.get(url=url)

        if r.status_code == 200:

            doc = BeautifulSoup(r.text, "html.parser")

            m = doc.find_all(class_="title__element headlineMain__title")

            manchete = m[0].text.strip()

            link = doc.find_all(class_="hyperlink headlineMain__link")

            rx = re.search(
                "(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])",
                str(link[0]),
            )

            link_uol = rx[0].strip()

            return r.status_code, manchete, link_uol
        else:
            retorno = {"status_code": r.status_code}
            return retorno

    @staticmethod
    def update_globo() -> list:
        url = "https://www.globo.com/"

        r = requests.get(url=url)

        if r.status_code == 200:

            doc = BeautifulSoup(r.text, "html.parser")

            m = doc.find_all(class_="post__title")

            manchete = m[0].text.strip().split(";")

            link = doc.find_all(class_="post__link")

            rx = re.search(
                "(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])",
                str(link[0]),
            )

            link = rx[0]

            return r.status_code, manchete[0], link
        else:
            retorno = {"status_code": r.status_code}
            return retorno

    @staticmethod
    def update_cnn() -> list:
        url = "https://www.cnnbrasil.com.br/"

        r = requests.get(url=url)

        if r.status_code == 200:

            doc = BeautifulSoup(r.text, "html.parser")

            m = doc.find_all(class_="home__title")

            manchete = re.search("[A-Z].*<", str(m[0]))

            manchete = manchete[0][:-1]

            link = doc.find_all(class_="home__post")

            rx = re.search(
                "(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])",
                str(link[0]),
            )

            link = rx[0]

            return r.status_code, manchete, link
        else:
            retorno = {"status_code": r.status_code}
            return retorno

    @staticmethod
    def send_email(assunto: str, html: str, *emails: str):
        corpo_email = f"{html}"
        msg = email.message.Message()
        msg["Subject"] = assunto
        msg["From"] = "caio.silva@shipay.com.br"
        msg["To"] = "caioviniciusxd@gmail.com"
        password = "murdpncfsorwliae"
        msg.add_header("Content-Type", "text/html")
        msg.set_payload(corpo_email)

        s = smtplib.SMTP("smtp.gmail.com: 587")
        s.starttls()
        # Login Credentials for sending the mail
        s.login(msg["From"], password)
        s.sendmail(msg["From"], [msg["To"]], msg.as_string().encode("utf-8"))

    @staticmethod
    def update_currency() -> map:
        url = "https://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL,BTC-BRL,BRL-RUB"
        r = requests.get(url=url)

        if r.status_code == 200:

            ld = json.loads(r.text)
            br_usd = ld["USDBRL"]["bid"]
            var_br_usd = ld["USDBRL"]["varBid"]
            br_eur = ld["EURBRL"]["bid"]
            var_br_eur = ld["EURBRL"]["varBid"]
            br_btc = ld["BTCBRL"]["bid"]
            var_br_btc = ld["BTCBRL"]["varBid"]
            br_rub = ld["BRLRUB"]["bid"]
            var_br_rub = ld["BRLRUB"]["varBid"]
            retorno = {
                "status_code": r.status_code,
                "price_dolar": br_usd,
                "var_dolar": var_br_usd,
                "price_euro": br_eur,
                "var_euro": var_br_eur,
                "price_btc": br_btc,
                "var_btc": var_br_btc,
                "price_rub": br_rub,
                "var_rub": var_br_rub,
            }

            return retorno
        else:
            retorno = {"status_code": r.status_code, "message": r.text}
            return retorno

    @staticmethod
    def update_meme() -> str:
        meme_link = (
            "https://www.ahnegao.com.br/wp-content/uploads/2022/02/meme-seg-2z-37.jpg"
        )
        return meme_link

    @staticmethod
    def update_quote() -> str:
        frase_do_dia = "Antes, a questão era descobrir se a vida precisava de ter algum significado para ser vivida. Agora, ao contrário, ficou evidente que ela será vivida melhor se não tiver significado."
        return frase_do_dia


app = Flask("newsletter")


@app.route("/")
def hello_world():
    moedas = Newsletter().update_currency()
    frase_do_dia = Newsletter().update_quote()
    meme_link = Newsletter().update_meme()
    globo = Newsletter().update_globo()
    uol = Newsletter().update_uol()
    cnn = Newsletter().update_cnn()
    return render_template(
        "index.html",
        moeda=moedas,
        frase=frase_do_dia,
        meme=meme_link,
        globolink=globo[2],
        globomanchete=globo[1],
        cnnlink=cnn[2],
        cnnmanchete=cnn[1],
        uollink=uol[2],
        uolmanchete=uol[1],
    )


@app.route("/addmember")
def addmember(name: str, email: str):
    Database().addmember(name, email)
    return "<p>Olá Bem vindo a NewsLetter Home!</p>"


app.run(host="0.0.0.0")
