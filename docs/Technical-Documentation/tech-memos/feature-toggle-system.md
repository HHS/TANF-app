# Feature Toggle System for TDP

**Audience**: TDP Software Engineers <br>
**Subject**: Generic Feature Toggle System with Admin Controls <br>
**Date**: November 19, 2024 <br>

## Summary

This technical memorandum describes the design and implementation of a generic feature toggle system for the TDP application. The system allows Django administrators to enable/disable features without code changes or deployments. Feature flags and their configurations are exposed to the React frontend via REST API, integrated with the existing authentication flow, and refreshed periodically. The system includes describes a comprehensive audit logging and model versioning system using a third party package or a generic audit log model if we cannot upgrade Django to v4.2 or greater.

**Key capabilities**:
- Toggle features on/off via Django admin interface
- Configure feature-specific settings via JSON `config` field
- Automatic propagation to frontend within a configurable time duration
- Full audit trail of all changes
- Generic, reusable architecture for future features

## Background

Currently, enabling or disabling features like PIA datafile submission requires code changes and deployment. This creates operational overhead and prevents rapid response to issues. The feature toggle system addresses this by:

1. **Decoupling feature availability from code deployments** - Admins can toggle features instantly
2. **Providing runtime configuration** - Feature behavior can be adjusted without code changes
3. **Enabling gradual rollouts** - Features can be tested with subsets of users
4. **Supporting emergency rollbacks** - Problematic features can be disabled immediately
5. **Maintaining audit compliance** - All changes are logged with full context

## Out of Scope

The following are explicitly out of scope for this implementation and should be considered in separate technical memorandums:

- **User-specific feature flags** - This system provides global flags; per-user or per-group targeting requires additional work and should use the existing permissions system
- **Feature flag lifecycle management** - Automated cleanup of old/unused flags is not implemented
- **Real-time flag updates** - Changes propagate on configurable schedule

## Method/Design

### Architecture Overview

The feature toggle system consists of four main components:

1. **Django Backend** - `FeatureFlag` model, admin interface, helper functions, REST API
2. **Generic Audit System** - Package implementation or custom approach (not recommended)
3. **React Frontend** - Redux state management, API integration, React hooks
4. **Caching Layer** - Redis-backed caching

## Backend
### Data Model Design

#### FeatureFlag Model

The `FeatureFlag` model is the core of the system.

**Location**: `tdrs-backend/tdpservice/core/models/feature_flag.py`

```python
class FeatureFlag(models.Model):
    class Meta:
        ordering = ['feature_name']
        verbose_name = 'Feature Flag'
        verbose_name_plural = 'Feature Flags'

    feature_name = models.CharField(max_length=100, unique=True, db_index=True)
    enabled = models.BooleanField(default=False)
    config = models.JSONField(null=False, blank=False, default=dict)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Design rationale**:
- `feature_name`: Unique identifier, indexed for fast lookups
- `enabled`: Boolean toggle, defaults to `False` for safety
- `config`: Flexible JSON configuration for feature-specific settings, cannot be null to avoid NoneType errors
- `description`: Human-readable documentation for admins
- Timestamps: Audit trail for when features were created/modified

**Suggested Naming convention**:
To have a consistent feature naming convention this memo recommends using the "domain" and "action" format.
The domain can be treated similarly to a web domain and contain sub-domains to keep feature names short, descriptive and unique.
`{domain}_{subdomain}_{action}` (e.g., `datafiles_pia_submission`, `reports_feedback`)

### Django Admin Interface

The admin interface for `FeatureFlag`s will need to provide a user friendly interface. The default interface the Django Admin Console (DAC)
provides for editing JSON fields is sufficient when it is infrequent or when the JSON is simple. However, because the
`FeatureFlag` model will contain a JSON `config` field that can be arbitrarily complex, we should provide a more user friendly
interface for editing it to help avoid errors. The `django-json-widget` package provides a visual JSON editor with syntax highlighting and validation.
Integrating this into the DAC form for the `FeatureFlag` will greatly improve the user experience. An example admin class
is provided below.

**Location**: `tdrs-backend/tdpservice/core/admin.py`

```python
class FeatureFlagAdminForm(ModelForm):
    class Meta:
        model = FeatureFlag
        fields = '__all__'
        widgets = {
            'config': JSONEditorWidget(options={
                'mode': 'code',
                'modes': ['code', 'tree'],
                'search': True
            })
        }

@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    form = FeatureFlagAdminForm

    list_display = ['feature_name', 'updated_at']
    list_filter = ['enabled', 'created_at', 'updated_at']
    search_fields = ['feature_name', 'description']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Feature Identity', {
            'fields': ('feature_name', 'description')
        }),
        ('Configuration', {
            'fields': ('enabled', 'config'),
            'description': 'Toggle the feature on/off and configure feature-specific settings'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # Only allow superusers to delete features
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
```

**Dependencies**:
```python
django-json-widget
```

### Caching

Because we will have many clients querying this information on a regular basis it makes sense to leverage caching to keep
the latency for the clients as low as possible. Since we already implement Redis, but hardly leverage it, caching the feature
flags in Redis will help us keep the latency low. Django's cache framework provides the abstraction around Redis and other caches,
which makes implementing a cache service to handle multiple cache instances quite easy.

**Caching strategy**:
- Individual flags cached for `DEFAULT_CACHE_TIMEOUT` seconds
- Bulk "all flags" query cached for `DEFAULT_CACHE_TIMEOUT` seconds
- Cache automatically updated on feature flag save/delete via Django signals

**Performance impact**:
- Without caching: ~10-20ms per check (DB query)
- With caching: ~0.1-1ms per check (cache hit)
- Cache hit rate expected: >99% in steady state

**Location**: `tdrs-backend/tdpservice/settings/common.py`
```python
DEFAULT_CACHE_TIMEOUT = 300
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'tdp-features',
        'TIMEOUT': DEFAULT_CACHE_TIMEOUT,
    }
}
```

Note: This config would need to be overridden for the deployed environments.

**Location**: `tdrs-backend/tdpservice/core/services/cache.py`
```python
from typing import Any, Optional, Callable
from django.core.cache import caches
from django.core.cache.backends.base import BaseCache
import logging

logger = logging.getLogger(__name__)


class CacheService:
    """
    Service class for interacting with Django's cache framework.

    Provides a clean abstraction for cache operations with support for
    multiple cache backends, automatic key prefixing, and error handling.
    """

    def __init__(self, cache_name: str = 'default', key_prefix: str = ''):
        self.cache_name = cache_name
        self.key_prefix = key_prefix
        self.cache = self._init_cache()

    def _init_cache(self) -> BaseCache:
        """Load cache backend."""
        try:
            self.cache = caches[self.cache_name]
        except Exception as e:
            logger.exception(f"Failed to access cache '{self.cache_name}'")
            # Fall back to default cache
            self.cache = caches['default']
        return self.cache

    def _make_key(self, key: str) -> str:
        """Generate full cache key with prefix."""
        if self.key_prefix:
            return f"{self.key_prefix}:{key}"
        return key

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve value from cache."""
        try:
            full_key = self._make_key(key)
            value = self.cache.get(full_key, default)
            logger.debug(f"Cache GET '{full_key}': {'HIT' if value is not None else 'MISS'}")
            return value
        except Exception as e:
            logger.exception(f"Cache GET error for key '{key}'")
            return default

    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """Store value in cache."""
        try:
            full_key = self._make_key(key)
            self.cache.set(full_key, value, timeout)
            logger.debug(f"Cache SET '{full_key}' (timeout={timeout})")
            return True
        except Exception as e:
            logger.exception(f"Cache SET error for key '{key}'")
            return False

    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            full_key = self._make_key(key)
            self.cache.delete(full_key)
            logger.debug(f"Cache DELETE '{full_key}'")
            return True
        except Exception as e:
            logger.exception(f"Cache DELETE error for key '{key}'")
            return False

    def get_or_set(self, key: str, default: Callable[[], Any],
                   timeout: Optional[int] = None) -> Any:
        """Get value from cache, or compute and cache it if not found."""
        try:
            full_key = self._make_key(key)
            value = self.cache.get_or_set(full_key, default, timeout)
            logger.debug(f"Cache GET_OR_SET '{full_key}'")
            return value
        except Exception as e:
            logger.exception(f"Cache GET_OR_SET error for key '{key}'")
            # Fall back to computing value
            return default() if callable(default) else default

    def get_many(self, keys: list[str]) -> dict[str, Any]:
        """Retrieve multiple values from cache."""
        try:
            full_keys = [self._make_key(k) for k in keys]
            values = self.cache.get_many(full_keys)

            # Strip prefix from returned keys
            if self.key_prefix:
                prefix_len = len(self.key_prefix) + 1
                values = {k[prefix_len:]: v for k, v in values.items()}

            logger.debug(f"Cache GET_MANY: {len(values)}/{len(keys)} hits")
            return values
        except Exception as e:
            logger.exception(f"Cache GET_MANY error")
            return {}

    def set_many(self, data: dict[str, Any], timeout: Optional[int] = None) -> bool:
        """Store multiple values in cache."""
        try:
            full_data = {self._make_key(k): v for k, v in data.items()}
            self.cache.set_many(full_data, timeout)
            logger.debug(f"Cache SET_MANY: {len(data)} keys (timeout={timeout})")
            return True
        except Exception as e:
            logger.exception(f"Cache SET_MANY error")
            return False

    def delete_many(self, keys: list[str]) -> bool:
        """Delete multiple values from cache."""
        try:
            full_keys = [self._make_key(k) for k in keys]
            self.cache.delete_many(full_keys)
            logger.debug(f"Cache DELETE_MANY: {len(keys)} keys")
            return True
        except Exception as e:
            logger.exception(f"Cache DELETE_MANY error")
            return False

    def clear(self) -> bool:
        """Clear all values from cache."""
        try:
            self.cache.clear()
            logger.warning(f"Cache CLEAR: entire '{self.cache_name}' cache cleared")
            return True
        except Exception as e:
            logger.exception(f"Cache CLEAR error")
            return False

    def has_key(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            full_key = self._make_key(key)
            return self.cache.has_key(full_key)
        except Exception as e:
            logger.exception(f"Cache HAS_KEY error for key '{key}'")
            return False

    def touch(self, key: str, timeout: Optional[int] = None) -> bool:
        """Update the timeout for a key without changing its value."""
        try:
            full_key = self._make_key(key)
            result = self.cache.touch(full_key, timeout)
            logger.debug(f"Cache TOUCH '{full_key}' (timeout={timeout})")
            return result
        except Exception as e:
            logger.exception(f"Cache TOUCH error for key '{key}'")
            return False


# Convenience instances for common use cases
default_cache = CacheService()
feature_cache = CacheService(key_prefix='feature_flag')
```

This generic approach is initially more complex than what the feature flag system requires. However, it lays the foundation
to grow the caching architecture without potentially more costly re-factors.

#### Automated Cache Updates

Feature flags will be primarily managed via the admin console. When a feature flag is created, updated, or deleted the cache becomes
invalid and requires an appropriate update. This can be easily handled with signals. See an example below of a signal receiver for the
`post_save` signal. The same pattern can be applied to the `post_delete` signal to delete keys as necessary.

**Location**: `tdrs-backend/tdpservice/core/signals.py`

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import FeatureFlag
from .services import feature_cache
import logging

logger = logging.getLogger(__name__)

@receiver([post_save], sender=FeatureFlag)
def update_feature_flag_cache(sender, instance, **kwargs):
    """Update feature flag in cache when feature flags are modified."""
    logger.info(
        f"Feature flag '{instance.feature_name}' saved. "
        f"Updating cache. New state: {instance.enabled}"
    )

    value = {
        'enabled': instance.enabled,
        'config': instance.config
    }

    feature_cache.set(instance.feature_name, value)
```


### Feature Flag Auditing
Because the feature flag system allows changes to be made that will affect production that do not go through a formal review process,
having a method to audit and rollback those changes is a necessity. The TDP backend has a model, `ChangeRequestAuditLog`, that is used
for a similar purpose. However, the `ChangeRequestAuditLog` interface is tightly coupled to user change requests and does not allow an admin
to rollback a change based on the change logged in the audit log. This is a common requirement for applications and is well supported by
existing tools. This technical memorandum recommends implementing either `django-simple-history` or `django-reversion` to provide audit logging,
robust versioning and rollback capabilities for `FeatureFlag`s and any other model in the future that requires it. The caveat here is that
the TDP backend is running off of Django v3.2 and these packages require Django >v4.2. With that in mind this technical memorandum suggests
the Dev team takes the time to upgrade the backend dependencies to support Django >v4.2. If this cannot be accommodated then the Dev team should
investigate other options for audit logging and versioning.


### Serialization and View(s)

The api endpoint for feature flags should only support GET and LIST actions. Access to the features endpoint should be
protected by the `IsAuthenticated` permission.

**Location**: `tdrs-backend/tdpservice/core/serializers.py`

```python
from rest_framework import serializers

class FeatureFlagSerializer(serializers.Serializer):
    """Serializer for feature flag data exposed to frontend."""
    enabled = serializers.BooleanField()
    config = serializers.JSONField(allow_null=False, required=False)
```

**Location**: `tdrs-backend/tdpservice/core/views.py`

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .services import feature_cache
from .serializers import FeatureFlagSerializer
import logging

logger = logging.getLogger(__name__)

def get_all_feature_flags() -> Dict[str, Dict[str, Any]]:
    """Get all feature flags. """
    cache_key = "feature_flags:all"
    cached = feature_cache.get(cache_key)

    if cached is not None:
        return cached

    flags = FeatureFlag.objects.all()
    result = {
        flag.feature_name: {
            'enabled': flag.enabled,
            'config': flag.config
        }
        for flag in flags
    }

    feature_cache.set(cache_key, result, DEFAULT_CACHE_TIMEOUT)
    return result

class FeatureFlagsView(APIView):
    """View for retrieving all feature flags."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        key = request.query_params.get('key')
        if not key:
            flags = get_all_feature_flags()
            serialized = {
                name: FeatureFlagSerializer(data).data
                for name, data in flags.items()
            }
            return Response(serialized)
        flag = feature_cache.get(key)
        if flag is None:
            return Response({key: {}})
        serializer = FeatureFlagSerializer(flag)
        return Response({key: serializer.data})
```

Note that the `get_all_feature_flags` function is not performing any exception handling. While the cache service does have handling
internally, in the case that Redis is unavailable the view should perform its own exception handling and fallback handling to ensure
a proper response is returned to the frontend.


## Frontend
### Redux Implementation

To support the admin based feature flag CRUD operations, the frontend will need to implement an automatic refresh of the flags
to ensure users are using the most up to date features. Because the flags are not expected to change that frequently, the Redux
store is a good place to keep them while asynchronously checking for updates every so often. TDP already follows a similar pattern
via it's "auth check" thunk. This technical memorandum recommends a similar approach for the feature flags.

**Location**: `tdrs-frontend/src/actions/featureFlags.js` and `tdrs-frontend/src/reducers/featureFlags.js`

**Action types**:
- `FETCH_FEATURE_FLAGS` - Start fetching
- `SET_FEATURE_FLAGS` - Store fetched flags
- `SET_FEATURE_FLAGS_ERROR` - Store error
- `CLEAR_FEATURE_FLAGS_ERROR` - Clear error
- `RESET_FEATURE_FLAGS` - Clear all flags (on logout)

**State shape**:
```javascript
{
  featureFlags: {
    flags: {
      pia_submission: { enabled: true, config: {...} }
    },
    loading: false,
    error: null,
    lastFetched: 1700251234567,
  }
}
```

**Example Thunk**:
```javascript
export const fetchFeatureFlags = () => async (dispatch) => {
  dispatch({ type: FETCH_FEATURE_FLAGS })
  try {
    const { data } = await axiosInstance.get(`${BACKEND_URL}/v1/features/`)
    dispatch({ type: SET_FEATURE_FLAGS, payload: { flags: data } })
  } catch (error) {
    dispatch({ type: SET_FEATURE_FLAGS_ERROR, payload: { error } })
  }
}
```

### Auth Check Integration

Because the feature flags are dependent on the auth state of the user, it makes sense to couple the execution of the `fetchAuth`
with the handling of the feature flags. That is, when a user authenticates successfully, we should immediately fetch the feature
flags and populate the redux store. Conversely, if the user does not successfully authenticate we should ensure the feature state
is cleared. Because the auth check also runs via the `IdleTimer` we can guarantee a consistent and timely update to the feature
flag state.

**Location**: `tdrs-frontend/src/actions/auth.js`

```javascript
export const fetchAuth = () => async (dispatch) => {
  dispatch({ type: FETCH_AUTH })
  // ...Existing code
  if (data?.user) {
    // ...Existing code
    // Update feature flags
    dispatch(fetchFeatureFlags())
  } else {
    // ...Existing code
    // Clear feature flags
    dispatch(resetFeatureFlags())
  }
}
```

### Periodic Refresh Strategy

In the event that the this pattern becomes more frequent, or the implementer decides not to couple the auth check with the
feature flag update. This technical memorandum suggest a generic data component that will handle the interval based redux
updates.

**Example Component**:
```javascript
const ReduxRefresh = ({ thunk, intervalMs = 300000 }) => {
  const dispatch = useDispatch()
  const isAuthenticated = useSelector((state) => state.auth.authenticated)

  useEffect(() => {
    if (!isAuthenticated) return // Should probably clear redux state here

    const interval = setInterval(() => {
      dispatch(thunk)
    }, intervalMs)

    return () => clearInterval(interval)
  }, [isAuthenticated, intervalMs, dispatch])

  return null
}
```

### Frontend React Hooks

Continuing the frontend's effort to move re-useable state and logic to hooks, a `useFeatureFlag` hook is suggested to allow
components easy abstracted access to the feature flags redux state.

**Location**: `tdrs-frontend/src/hooks/useFeatureFlag.js`

```javascript
import { useSelector } from 'react-redux';

export const useFeatureFlag = (featureName) => {

  const flags = useSelector(state => state.featureFlags.flags)

  const getFlag = (featureName) => {
    // Note we don't store flags in a state variable to ensure the hook always accesses the latest redux state
    return flags[featureName]
  }

  const getFlags = () => {
    return flags
  }

  return {
    getFlag,
    getFlags,
  }
};
```

### Feature Gating

Similar to the PrivateRoute component, the frontend needs a consistent way to enable/disable features based on the redux
state. The minimal gate component below is recommended to allow easy feature gating.

**Location**: `tdrs-frontend/src/components/FeatureGate.js`

```javascript
const FeatureGate = ({ feature, children, fallback = null }) => {
  const isEnabled = useFeatureFlag(feature);
  return isEnabled ? children : fallback;
};
```

## Affected Systems

This feature will affect the following systems:

### Backend
- **Django Core App** - New models, admin, utils, views, signals
- **Database** - New tables: `feature_flags`, audit tables from auditing/versioning package
- **Redis Cache** - New cache keys for feature flags
- **REST API** - New endpoint `/api/v1/features/`

### Frontend
- **Redux Store** - New `featureFlags` actions/reducers
- **Auth Flow** - Modified to fetch feature flags on login
- **Components** - Updating and creating components to support feature gating and redux updating

## Test Cases

### Backend Tests
- `FeatureFlag` model validation
- `FeatureFlag` CRUD operations and cache validity
- `CacheService` coverage tests
- Audit/version object creation on `FeatureFlag` CRUD operations
- `FeatureFlag` api tests

### Frontend Tests
- Action/Reducer coverage tests
- `ReduxRefresh` component testing if implemented
- `useFeatureFlag` coverage tests
- `FeatureGate` coverage tests

## Conclusion

The feature toggle system provides a robust, scalable solution for runtime feature management in TDP. By decoupling feature availability from code deployments, it enables faster iteration, safer rollouts, and immediate response to issues with new features. The generic audit logging system ensures traceability, versioning, and rollback capabilities. The system is designed to be extensible, allowing easy addition of new features.
