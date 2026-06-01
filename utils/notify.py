"""
Android notification helper using jnius directly.
Works in both Activity (app open/background) and Service (app closed) contexts.
"""
import os

CHANNEL_ID = 'todo_reminder'
NOTIF_ID = 42
_log_path = os.path.join(
    os.environ.get('ANDROID_PRIVATE', os.path.expanduser('~')),
    'notif.log',
)


def _log(msg):
    try:
        from datetime import datetime
        with open(_log_path, 'a') as f:
            f.write(f"{datetime.now()}: {msg}\n")
    except Exception:
        pass


def send_notification(title, message):
    try:
        from jnius import autoclass

        # Resolve Android context — Activity first, then Service
        context = None
        try:
            ctx = autoclass('org.kivy.android.PythonActivity').mActivity
            if ctx is not None:
                context = ctx
        except Exception:
            pass
        if context is None:
            try:
                ctx = autoclass('org.kivy.android.PythonService').mService
                if ctx is not None:
                    context = ctx
            except Exception:
                pass
        if context is None:
            _log("ERROR: no Android context available")
            return False

        _log(f"Context: {context.getClass().getName()}")

        NotificationManager = autoclass('android.app.NotificationManager')
        NotificationChannel = autoclass('android.app.NotificationChannel')
        NotificationBuilder = autoclass('android.app.Notification$Builder')

        nm = context.getSystemService(context.NOTIFICATION_SERVICE)

        # Create channel (idempotent)
        channel = NotificationChannel(
            CHANNEL_ID,
            'Rappels Todo',
            NotificationManager.IMPORTANCE_DEFAULT,
        )
        nm.createNotificationChannel(channel)

        # Safe icon: prefer app icon, fall back to system ic_dialog_info
        icon_id = context.getApplicationInfo().icon
        if not icon_id:
            icon_id = autoclass('android.R$drawable').ic_dialog_info

        builder = NotificationBuilder(context, CHANNEL_ID)
        builder.setSmallIcon(icon_id)
        builder.setContentTitle(title)
        builder.setContentText(message)
        builder.setAutoCancel(True)

        nm.notify(NOTIF_ID, builder.build())
        _log("Notification posted successfully")
        return True

    except Exception as e:
        import traceback
        _log(f"ERROR: {traceback.format_exc()}")
        return False
