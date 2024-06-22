import os

PATH = "/".join(__file__.split("/")[:-1])


MENU_XML = open(f"{PATH}/ui/menu.xml").read()
LICENSE = open(f"{PATH}/../LICENSE").read()
MAIN_CSS = f"{PATH}/ui/styles/main.css"
