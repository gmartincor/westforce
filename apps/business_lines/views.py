from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Sum, Count

from .models import BusinessLine
from .services import BusinessLineService


class BusinessLineListView(LoginRequiredMixin, ListView):
    model = BusinessLine
    template_name = 'business_lines/list.html'
    context_object_name = 'business_lines'
    
    def get_queryset(self):
        return BusinessLine.objects.filter(is_active=True).order_by('level', 'order', 'name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = BusinessLineService()
        context['tree_data'] = service.get_business_lines_tree()
        return context


class BusinessLineDetailView(LoginRequiredMixin, DetailView):
    model = BusinessLine
    template_name = 'business_lines/detail.html'
    context_object_name = 'business_line'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        business_line = self.get_object()
        
        context['income_stats'] = {
            'total_revenue': business_line.total_income,
            'service_count': business_line.income_count,
            'recent_incomes': business_line.incomes.order_by('-date')[:10]
        }
        
        return context


class BusinessLineCreateView(LoginRequiredMixin, CreateView):
    model = BusinessLine
    template_name = 'business_lines/form.html'
    fields = ['name', 'parent', 'description', 'location', 'order']
    success_url = reverse_lazy('business_lines:list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Create Business Line'
        return context


class BusinessLineUpdateView(LoginRequiredMixin, UpdateView):
    model = BusinessLine
    template_name = 'business_lines/form.html'
    fields = ['name', 'parent', 'description', 'location', 'order', 'is_active']
    success_url = reverse_lazy('business_lines:list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Edit Business Line'
        return context


class BusinessLineDeleteView(LoginRequiredMixin, DeleteView):
    model = BusinessLine
    template_name = 'business_lines/confirm_delete.html'
    success_url = reverse_lazy('business_lines:list')
