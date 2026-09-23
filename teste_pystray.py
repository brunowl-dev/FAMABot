import pystray
from PIL import Image

def sair(icon, item):
    icon.stop()

def teste(icon, item):
    print("teste")    

# cria uma imagem simples 64x64 só pra servir de ícone
imagem = Image.new("RGB", (64, 64), color="green")

menu = pystray.Menu(
    pystray.MenuItem("Sair", sair),
    pystray.MenuItem("Teste", teste)
)

icone = pystray.Icon("fama_notify", imagem, "FAMA Notificações", menu)
icone.run()