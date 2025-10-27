from ..core.services.base import BaseService, ValidationMixin
from .models import BusinessLine
from typing import Dict, List, Optional, Set
from django.db.models import QuerySet


class BusinessLineService(BaseService, ValidationMixin):
    
    def __init__(self):
        super().__init__(BusinessLine)
    
    def get_active_business_lines(self) -> QuerySet:
        return self.get_all(is_active=True)
    
    def get_by_level(self, level: int) -> QuerySet:
        return self.get_all(level=level, is_active=True)
    
    def get_root_business_lines(self) -> QuerySet:
        return self.get_all(parent__isnull=True, is_active=True)
    
    def get_children(self, parent_id: int) -> QuerySet:
        return self.get_all(parent_id=parent_id, is_active=True)
    
    def get_business_lines_tree(self) -> List[Dict]:
        return self.get_hierarchy_tree()
    
    def get_hierarchy_tree(self) -> List[Dict]:
        root_lines = self.get_root_business_lines().order_by('order', 'name')
        
        def build_tree(business_lines):
            tree = []
            for line in business_lines:
                children = self.get_children(line.id)
                tree_item = {
                    'id': line.id,
                    'name': line.name,
                    'slug': line.slug,
                    'location': line.location,
                    'level': line.level,
                    'description': line.description,
                    'children': build_tree(children) if children.exists() else []
                }
                tree.append(tree_item)
            return tree
        
        return build_tree(root_lines)
    
    def get_all_descendant_ids(self, business_line_id: int) -> Set[int]:
        business_line = self.get_by_id(business_line_id)
        if not business_line:
            return set()
        return business_line.get_descendant_ids()
    
    def create_business_line(self, **data) -> BusinessLine:
        level = data.get('level', 1)
        if level < 1 or level > 3:
            raise ValueError("Business line level must be between 1 and 3")
        
        return self.create(**data)
    
    def get_service_locations(self) -> List[str]:
        locations = self.get_active_business_lines().exclude(
            location__exact=''
        ).values_list('location', flat=True).distinct()
        
        return sorted([loc for loc in locations if loc])
    
    def get_business_lines_with_income(self, year: Optional[int] = None) -> QuerySet:
        queryset = self.get_active_business_lines()
        
        if year:
            return queryset.filter(incomes__accounting_year=year).distinct()
        
        return queryset.filter(incomes__isnull=False).distinct()
