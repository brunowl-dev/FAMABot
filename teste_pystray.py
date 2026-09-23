import pystray
from PIL import Image
from winotify import Notification

def sair(icon, item):
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

# cria uma imagem simples 64x64 só pra servir de ícone
imagem = Image.open("logo.png")

menu = pystray.Menu(
    pystray.MenuItem("Sair", sair),
    pystray.MenuItem("Teste Fiscal", lambda icon, item: notifica_setor(icon, setor="Fiscal")),
    pystray.MenuItem("Teste RH", lambda icon, item: notifica_setor(icon, setor="RH")),
    pystray.MenuItem("Teste Contábil", lambda icon, item: notifica_setor(icon, setor="Contábil"))
)

icone = pystray.Icon("fama_notificacoes", imagem, "FAMA Notificações", menu)
icone.run()