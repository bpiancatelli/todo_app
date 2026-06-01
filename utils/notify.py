"""
Android notification helper using jnius directly.
Works in both Activity (app open/background) and Service (app closed) contexts.
"""

CHANNEL_ID = 'todo_reminder'
NOTIF_ID = 42


def send_notification(title, message):
    try:
        from jnius import autoclass

        # Resolve Android context — Activity first, then Service
        context = None
        try:
            context = autoclass('org.kivy.android.PythonActivity').mActivity
        except Exception:
            pass
        if context is None:
            try:
                context = autoclass('org.kivy.android.PythonService').mService
            except Exception:
                pass
        if context is None:
            return False

        NotificationManager = autoclass('android.app.NotificationManager')
        NotificationChannel = autoclass('android.app.NotificationChannel')
        NotificationBuilder = autoclass('android.app.Notification$Builder')

        nm = context.getSystemService(context.NOTIFICATION_SERVICE)

        # Create channel (idempotent — safe to call on every notification)
        channel = NotificationChannel(
            CHANNEL_ID,
            'Rappels Todo',
            NotificationManager.IMPORTANCE_DEFAULT,
        )
        nm.createNotificationChannel(channel)

        icon_id = context.getApplicationInfo().icon
        builder = NotificationBuilder(context, CHANNEL_ID)
        builder.setSmallIcon(icon_id)
        builder.setContentTitle(title)
        builder.setContentText(message)
        builder.setAutoCancel(True)

        nm.notify(NOTIF_ID, builder.build())
        return True
    except Exception:
        return False
