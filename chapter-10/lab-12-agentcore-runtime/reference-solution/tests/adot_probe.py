"""ADOT bootstrap probe with real SDK span callbacks and console export only."""

import socket

from agents import agent_span, function_span, generation_span, trace
from opentelemetry import trace as otel_trace

from telemetry import instrument_agents


def deny_network(*args, **kwargs):
    raise AssertionError("offline probe blocked network")


socket.socket.connect = deny_network
socket.socket.connect_ex = deny_network
instrument_agents()
with trace("offline_adot_probe"):
    with agent_span("course_assistant"):
        with generation_span(model="offline_fixture"):
            pass
        with function_span("get_course_info"):
            pass
otel_trace.get_tracer_provider().force_flush()
