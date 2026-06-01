"""
Schedule daily notification using AlarmManager.
This is more reliable than a persistent service on Samsung devices
which aggressively kill background processes.
"""
import os

_ALARM_REQUEST_CODE = 1001


def _get_service_class(context):
    from jnius import autoclass
    package = context.getPackageName()
    # p4a generates service class as Service + name with first letter capitalised
    for suffix in ['ServiceTodonotification', 'ServiceTodoNotification']:
        try:
            return autoclass(f'{package}.{suffix}')
        except Exception:
            pass
    return None


def schedule_alarm(context, hour, minute):
    """Schedule (or reschedule) the notification alarm for next occurrence of hour:minute."""
    try:
        from jnius import autoclass
        from datetime import datetime, timedelta

        AlarmManager = autoclass('android.app.AlarmManager')
        PendingIntent = autoclass('android.app.PendingIntent')
        Intent = autoclass('android.content.Intent')
        Build = autoclass('android.os.Build')

        svc_cls = _get_service_class(context)
        if svc_cls is None:
            return False

        intent = Intent(context, svc_cls)
        intent.putExtra('python_service_argument', 'alarm_trigger')

        flags = PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        if Build.VERSION.SDK_INT >= 26:
            pending = PendingIntent.getForegroundService(
                context, _ALARM_REQUEST_CODE, intent, flags
            )
        else:
            pending = PendingIntent.getService(
                context, _ALARM_REQUEST_CODE, intent, flags
            )

        now = datetime.now()
        scheduled = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if scheduled <= now:
            scheduled += timedelta(days=1)
        trigger_ms = int(scheduled.timestamp() * 1000)

        am = context.getSystemService(context.ALARM_SERVICE)
        # setAndAllowWhileIdle fires in Doze mode, no special permission needed
        am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, trigger_ms, pending)
        return True
    except Exception:
        return False


def cancel_alarm(context):
    """Cancel any scheduled notification alarm."""
    try:
        from jnius import autoclass

        PendingIntent = autoclass('android.app.PendingIntent')
        Intent = autoclass('android.content.Intent')
        Build = autoclass('android.os.Build')
        AlarmManager = autoclass('android.app.AlarmManager')

        svc_cls = _get_service_class(context)
        if svc_cls is None:
            return

        intent = Intent(context, svc_cls)
        flags = PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        if Build.VERSION.SDK_INT >= 26:
            pending = PendingIntent.getForegroundService(
                context, _ALARM_REQUEST_CODE, intent, flags
            )
        else:
            pending = PendingIntent.getService(
                context, _ALARM_REQUEST_CODE, intent, flags
            )
        am = context.getSystemService(context.ALARM_SERVICE)
        am.cancel(pending)
    except Exception:
        pass
