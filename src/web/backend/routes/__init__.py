"""Routes package"""
from src.web.backend.routes.models import ModelsResource, ModelDetailResource, ModelUploadResource
from src.web.backend.routes.segment import SegmentResource, BatchSegmentResource, SegmentHistoryResource
from src.web.backend.routes.visualization import VisualizationResource, GPUMonitorResource
from src.web.backend.routes.auth import LoginResource
from src.web.backend.routes.augmentation import AugmentationPreviewResource
from src.web.backend.routes.profile import ProfileResource, AvatarResource, PasswordResource
from src.web.backend.routes.settings import SystemConfigResource, StorageInfoResource, LogsResource

__all__ = [
    'ModelsResource', 'ModelDetailResource', 'ModelUploadResource',
    'SegmentResource', 'BatchSegmentResource', 'SegmentHistoryResource',
    'VisualizationResource', 'GPUMonitorResource',
    'LoginResource',
    'AugmentationPreviewResource',
    'ProfileResource', 'AvatarResource', 'PasswordResource',
    'SystemConfigResource', 'StorageInfoResource', 'LogsResource'
]
