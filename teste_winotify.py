from winotify import Notification

toast = Notification(
    app_id="FAMA Notificações",
    title="Novo atendimento",
    msg="Cliente selecionou o setor Fiscal",
    icon=r"c:/users/visitante/Documents/FAMABot/logo.png"
)
toast.show()