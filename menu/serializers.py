# menu/serializers.py

from rest_framework import serializers

from .models import Category, MenuItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description"]


class MenuItemSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = MenuItem
        fields = [
            "id",
            "category",
            "name",
            "description",
            "price",
            "stock",
            "low_stock_threshold",
            "available",
            "image",
        ]
        # Remove available from read_only_fields to allow updates
        # read_only_fields = ["available"]

    def to_representation(self, instance):
        """Custom representation to return full image URLs"""
        data = super().to_representation(instance)
        if instance.image:
            request = self.context.get("request")
            if request:
                data['image'] = request.build_absolute_uri(instance.image.url)
            else:
                data['image'] = instance.image.url
        return data
