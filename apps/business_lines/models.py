from django.db import models
from django.utils.text import slugify
from apps.core.models import TimeStampedModel

__all__ = ['BusinessLine']


class BusinessLine(TimeStampedModel):
    
    name = models.CharField(
        max_length=255,
        verbose_name="Business line name"
    )
    
    slug = models.SlugField(
        max_length=255,
        verbose_name="URL slug"
    )
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="Parent business line",
        db_index=True
    )
    
    level = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Level"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    
    location = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Service location",
        help_text="e.g. East Perth, West Perth, Fremantle"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        db_index=True
    )
    
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Display order"
    )

    class Meta:
        db_table = 'business_lines'
        verbose_name = "Business line"
        verbose_name_plural = "Business lines"
        unique_together = [['name', 'parent'], ['slug', 'parent']]
        ordering = ['level', 'order', 'name']
        indexes = [
            models.Index(fields=['parent', 'level']),
            models.Index(fields=['is_active', 'level']),
            models.Index(fields=['slug']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(level__gte=1) & models.Q(level__lte=3),
                name='business_line_level_range'
            ),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        
        if self.parent is None:
            self.level = 1
        else:
            self.level = self.parent.level + 1
        
        if self.level > 3:
            raise ValueError("Maximum allowed level is 3")
        
        super().save(*args, **kwargs)
        
        self._update_descendants_levels()

    def _update_descendants_levels(self):
        BusinessLine.objects.filter(parent=self).update(level=self.level + 1)
        for child in self.children.all():
            child._update_descendants_levels()

    def _generate_unique_slug(self):
        base_slug = slugify(self.name)
        if not base_slug:
            base_slug = 'business-line'
        
        queryset = BusinessLine.objects.filter(parent=self.parent, slug=base_slug)
        if self.pk:
            queryset = queryset.exclude(pk=self.pk)
        
        if not queryset.exists():
            return base_slug
        
        counter = 1
        while True:
            new_slug = f"{base_slug}-{counter}"
            queryset = BusinessLine.objects.filter(parent=self.parent, slug=new_slug)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            
            if not queryset.exists():
                return new_slug
            
            counter += 1

    def __str__(self):
        hierarchy_prefix = "  " * (self.level - 1)
        return f"{hierarchy_prefix}{self.name}"

    def get_full_hierarchy(self):
        if self.parent:
            return f"{self.parent.get_full_hierarchy()} > {self.name}"
        return self.name

    def get_url_path(self):
        path_parts = []
        current = self
        
        while current:
            path_parts.insert(0, current.slug)
            current = current.parent
        
        return '/'.join(path_parts)

    @property
    def total_income(self):
        return self.incomes.aggregate(
            total=models.Sum('amount')
        )['total'] or 0

    @property
    def income_count(self):
        return self.incomes.count()

    def get_descendant_ids(self):
        descendant_ids = {self.id}
        self._collect_descendant_ids(descendant_ids)
        return descendant_ids
    
    def _collect_descendant_ids(self, id_set):
        children = BusinessLine.objects.filter(parent=self)
        for child in children:
            id_set.add(child.id)
            child._collect_descendant_ids(id_set)

    def get_monthly_income(self, year=None, month=None):
        from django.utils import timezone
        from django.db.models import Sum
        
        current_date = timezone.now()
        year = year or current_date.year
        month = month or current_date.month
        
        return self.incomes.filter(
            date__year=year,
            date__month=month
        ).aggregate(total=Sum('amount'))['total'] or 0
