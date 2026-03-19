from .job import (
    JobBase,
    JobCreate,
    JobUpdate,
    JobResponse,
    JobListResponse,
    JobFilterParams,
)
from .scan_run import (
    ScanRunCreate,
    ScanRunResponse,
    ScanRunDetailResponse,
    ScanStatusResponse,
)
from .ai_model_config import (
    AIModelConfigBase,
    AIModelConfigCreate,
    AIModelConfigUpdate,
    AIModelConfigResponse,
    AIModelConfigListResponse,
)
from .profile import (
    ExperienceSchema,
    EducationSchema,
    ProjectSchema,
    ProfileBase,
    ProfileCreate,
    ProfileUpdate,
    ProfileResponse,
)
from .resume import (
    ResumeBase,
    ResumeCreate,
    ResumeResponse,
    ResumeAdaptationRequest,
    ResumeAdaptationResponse,
)
from .email import (
    EmailBase,
    EmailCreate,
    EmailResponse,
    EmailDraftRequest,
    EmailDraftResponse,
    EmailSendRequest,
)
from .application import (
    ApplicationBase,
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
    ApplicationStats,
)
from .auth import UserRegister, UserLogin, UserResponse, TokenResponse, TokenData

__all__ = [
    # Job
    "JobBase",
    "JobCreate",
    "JobUpdate",
    "JobResponse",
    "JobListResponse",
    "JobFilterParams",
    # Scan
    "ScanRunCreate",
    "ScanRunResponse",
    "ScanRunDetailResponse",
    "ScanStatusResponse",
    # AI Config
    "AIModelConfigBase",
    "AIModelConfigCreate",
    "AIModelConfigUpdate",
    "AIModelConfigResponse",
    "AIModelConfigListResponse",
    # Profile
    "ExperienceSchema",
    "EducationSchema",
    "ProjectSchema",
    "ProfileBase",
    "ProfileCreate",
    "ProfileUpdate",
    "ProfileResponse",
    # Resume
    "ResumeBase",
    "ResumeCreate",
    "ResumeResponse",
    "ResumeAdaptationRequest",
    "ResumeAdaptationResponse",
    # Email
    "EmailBase",
    "EmailCreate",
    "EmailResponse",
    "EmailDraftRequest",
    "EmailDraftResponse",
    "EmailSendRequest",
    # Application
    "ApplicationBase",
    "ApplicationCreate",
    "ApplicationUpdate",
    "ApplicationResponse",
    "ApplicationStats",
    # Auth
    "UserRegister",
    "UserLogin",
    "UserResponse",
    "TokenResponse",
    "TokenData",
]
