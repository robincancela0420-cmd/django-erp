from django.shortcuts import render
from django.http import JsonResponse
from core.permissions import require_page_permission

@require_page_permission("material_master", "view")
def material_master_view(request):
    return JsonResponse({
        "module": "Material Master",
        "message": "Access Granted"
    })

@require_page_permission("material_master", "add")
def material_master_add_view(request):
    return JsonResponse({
        "module": "Material Master",
        "action": "add",
        "message": "Add Access granted",
    })

@require_page_permission("material_master", "edit")
def material_master_edit_view(request):
    return JsonResponse({
        "module": "Material Master",
        "action": "edit",
        "message": "Edit access granted",
    })

@require_page_permission("material_master", "delete")
def material_master_delete_view(request):
    return JsonResponse({
        "module": "Material Master",
        "action": "delete",
        "message": "Delete access granted"
    })