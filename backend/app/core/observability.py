"""可观测层 (M8)。OpenTelemetry 可选：未安装或关闭时退化为无操作 span，不影响主链路。"""
from contextlib import contextmanager

from app.config import get_settings

s = get_settings()

try:
    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

    _HAVE_OTEL = True
except Exception:  # pragma: no cover - 依赖可选
    _HAVE_OTEL = False

if _HAVE_OTEL and s.otel_enabled:
    _provider = TracerProvider(resource=Resource.create({"service.name": s.app_name}))
    _provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(_provider)
    _tracer = trace.get_tracer("chenxing")
else:
    _tracer = None


@contextmanager
def span(name: str):
    """统一埋点入口；无 OTel 时零开销穿透。"""
    if _tracer is None:
        yield None
    else:
        with _tracer.start_as_current_span(name) as sp:
            yield sp
