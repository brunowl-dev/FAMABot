import pystray
from PIL import Image
from winotify import Notification
import threading

parar = threading.Event()

def cria_notificacao(titulo, mensagem=""):
    return Notification(
        app_id="FAMA Notificações",
        title=titulo,
        msg=mensagem,
        icon=r"c:/users/visitante/Documents/FAMABot/logo.png"
    )

def sair(icon):
    parar.set()
    toast = cria_notificacao("Fechando o programa")
    toast.show()  
    icon.stop()

def notifica_setor(icon, setor):
    toast = cria_notificacao("Novo atendimento", f"Cliente selecionou o {setor}")
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
        toast = cria_notificacao("Alerta", "30 SEGUNDOS")
        toast.show()
        parar.wait(30)

t1 = threading.Thread(target=defineStray)
t2 = threading.Thread(target=esperaTempo)

def main(): 
    t1.start()
    t2.start()

if __name__ == "__main__":
    main()