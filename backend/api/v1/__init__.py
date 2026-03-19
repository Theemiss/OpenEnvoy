# WR|"""API v1 package."""
# KM|
# SX|from fastapi import APIRouter
# RW|
# XT|from .endpoints import (
# YN|    jobs_router,
# SX|    applications_router,
# VZ|    profile_router,
# ZZ|    emails_router,
# JT|    review_router,
# RP|    feedback_router,
# QB|    ai_costs_router,
# XP|    auth_router,
# JN|    ai_configs_router,
# NZ|    scans_router,
# KM|)
# RJ|
# BV|api_router = APIRouter()
# HX|
# HQ|api_router.include_router(jobs_router)
# MB|api_router.include_router(applications_router)
# NW|api_router.include_router(profile_router)
# ZW|api_router.include_router(ai_configs_router)
# NZ|api_router.include_router(scans_router)
# XW|api_router.include_router(emails_router)
# ZX|api_router.include_router(review_router)
# BX|api_router.include_router(feedback_router)
# QB|api_router.include_router(ai_costs_router)
# WZ|api_router.include_router(auth_router)
# HK|
# BB|__all__ = ["api_router"]
# HQ|
