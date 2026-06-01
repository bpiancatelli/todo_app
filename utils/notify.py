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
    _log("send_notification: entry")
    try:
        _log("send_notification: importing jnius")
        from jnius import autoclass
        _log("send_notification: jnius imported OK")

        context = None

        # Try Service context FIRST (avoids Activity JNI crash in service process)
        _log("send_notification: trying PythonService.mService")
        try:
            ctx = autoclass('org.kivy.android.PythonService').mService
            _log(f"send_notification: PythonService.mService = {ctx}")
            if ctx is not None:
                context = ctx
        except Exception as e:
            _log(f"send_notification: PythonService failed: {e}")

        # Fallback to Activity (when called from main app)
        if context is None:
            _log("send_notification: trying PythonActivity.mActivity")
            try:
                ctx = autoclass('org.kivy.android.PythonActivity').mActivity
                _log(f"send_notification: PythonActivity.mActivity = {ctx}")
                if ctx is not None:
                    context = ctx
            except Exception as e:
                _log(f"send_notification: PythonActivity failed: {e}")

        if context is None:
            _log("ERROR: no Android context available")
            return False

        _log(f"send_notification: context class = {context.getClass().getName()}")

        _log("send_notification: getting NotificationManager classes")
        NotificationManager = autoclass('android.app.NotificationManager')
        NotificationChannel = autoclass('android.app.NotificationChannel')
        NotificationBuilder = autoclass('android.app.Notification$Builder')
        _log("send_notification: classes loaded")

        nm = context.getSystemService(context.NOTIFICATION_SERVICE)
        _log("send_notification: got NotificationManager")

        channel = NotificationChannel(
            CHANNEL_ID,
            'Rappels Todo',
            NotificationManager.IMPORTANCE_DEFAULT,
        )
        nm.createNotificationChannel(channel)
        _log("send_notification: channel created")

        icon_id = context.getApplicationInfo().icon
        if not icon_id:
            icon_id = autoclass('android.R$drawable').ic_dialog_info

        builder = NotificationBuilder(context, CHANNEL_ID)
        builder.setSmallIcon(icon_id)
        builder.setContentTitle(title)
        builder.setContentText(message)
        builder.setAutoCancel(True)
        _log("send_notification: builder configured")

        nm.notify(NOTIF_ID, builder.build())
        _log("send_notification: notification posted successfully")
        return True

    except Exception as e:
        import traceback
        _log(f"send_notification: EXCEPTION: {traceback.format_exc()}")
        return False
