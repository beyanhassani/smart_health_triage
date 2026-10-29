"""Domain'e özgü hatalar."""


class AccessDeniedError(PermissionError):
    """Kullanıcının rolü bu işlem için yetkili değilse fırlatılır."""


class InvalidStatusTransitionError(ValueError):
    """İzin verilmeyen bir randevu durum geçişi denendiğinde fırlatılır."""


class AppointmentNotFoundError(LookupError):
    """Verilen id ile kayıtlı randevu bulunamadığında fırlatılır."""
