import pystray
from PIL import Image
from winotify import Notification
import threading
from pathlib import Path

PASTA_DO_TRAY = Path(__file__).parent
LOGO = PASTA_DO_TRAY / "assets" / "logo.png" 
parar = threading.Event()

def cria_notificacao(titulo, mensagem=""):
    return Notification(
        app_id="FAMA Notificações",
        title=titulo,
        msg=mensagem,
        icon=str(LOGO)
    )

def sair(icon):
    parar.set()
    toast = cria_notificacao("Fechando o programa")
    toast.show()  
    icon.stop()

def notifica_setor(icon, setor):
    toast = cria_notificacao("Novo atendimento", f"Cliente selecionou o {setor}")
    toast.show()

def define_tray():
    imagem = Image.open(LOGO)

    menu = pystray.Menu(
        pystray.MenuItem("Sair", sair),
        pystray.MenuItem("Teste Fiscal", lambda icon, item: notifica_setor(icon, setor="Fiscal")),
        pystray.MenuItem("Teste RH", lambda icon, item: notifica_setor(icon, setor="RH")),
        pystray.MenuItem("Teste Contábil", lambda icon, item: notifica_setor(icon, setor="Contábil"))
    )

    icone = pystray.Icon("fama_notificacoes", imagem, "FAMA Notificações", menu)
    icone.run()

def espera_tempo():
    while not parar.is_set():
        toast = cria_notificacao("Alerta", "30 SEGUNDOS")
        toast.show()
        parar.wait(30)

def main(): 
    aviso_trinta_seg = threading.Thread(target=espera_tempo, daemon=True)
    aviso_trinta_seg.start()
    define_tray()

if __name__ == "__main__":
    main()
    