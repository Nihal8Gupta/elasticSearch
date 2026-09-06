from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return self.update(
            is_deleted=True,
            deleted_at=timezone.now(),
        )

    def hard_delete(self):
        return super().delete()

    def alive(self):
        return self.filter(is_deleted=False)

    def deleted(self):
        return self.filter(is_deleted=True)


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(
            self.model,
            using=self._db,
        ).filter(is_deleted=False)


class AllObjectsManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(
            self.model,
            using=self._db,
        )


class SoftDeleteModel(BaseModel):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    objects = SoftDeleteManager()
    all_objects = AllObjectsManager()

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deleted_at = timezone.now()

        self.save(
            update_fields=[
                "is_deleted",
                "deleted_at",
                "updated_at",
            ]
        )

    def soft_delete(self):
        return self.delete()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None

        self.save(
            update_fields=[
                "is_deleted",
                "deleted_at",
                "updated_at",
            ]
        )

    def hard_delete(self, *args, **kwargs):
        return super().delete(*args, **kwargs)

    class Meta:
        abstract = True
