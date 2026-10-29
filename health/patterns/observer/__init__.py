"""Observer kalıbının somut gerçeklemesi."""
from .observers import DoctorObserver, PatientObserver
from .subject import AppointmentSubject

__all__ = ["AppointmentSubject", "DoctorObserver", "PatientObserver"]
