import pystray
from PIL import Image
from winotify import Notification
import time
import threading

parar = threading.Event()

def sair(icon, item):
    parar.set()
    toast = Notification(
    app_id="FAMA Notificações",
    title="Fechando o programa",
    icon=r"c:/users/visitante/Documents/FAMABot/logo.png"
    )
    toast.show()  
    icon.stop()

def notifica_setor(icon, setor):
    toast = Notification(
    app_id="FAMA Notificações",
    title="Novo atendimento",
    msg=f"Cliente selecionou o setor {setor}",
    icon=r"c:/users/visitante/Documents/FAMABot/logo.png"
    )
    toast.show()

def defineStray():
    imagem = Image.open("logo.png")

    menu = pystray.Menu(
        pystray.MenuItem("Sair", sair),
        pystray.MenuItem("Teste Fiscal", lambda icon, item: notifica_setor(icon, setor="Fiscal")),
        pystray.MenuItem("Teste RH", lambda icon, item: notifica_setor(icon, setor="RH")),
        pystray.MenuItem("Teste Contábil", lambda icon, item: notifica_setor(icon, setor="Contábil"))
    )

    icone = pystray.Icon("fama_notificacoes", imagem, "FAMA Notificações", menu)
    icone.run()

def esperaTempo():
    while not parar.is_set():
        toast = Notification(
        app_id="FAMA Notificações",
        title="Alerta",
        msg=f"10 SEGUNDOS",
        icon=r"c:/users/visitante/Documents/FAMABot/logo.png"
        )
        toast.show()
        parar.wait(10)

t1 = threading.Thread(target=defineStray)
t2 = threading.Thread(target=esperaTempo)

def main(): 
    t1.start()
    t2.start()

main()