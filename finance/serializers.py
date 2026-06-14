from rest_framework import serializers
from django.db import IntegrityError
from .models import Product, Payment


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    student_phone = serializers.CharField(write_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'enrollment', 'session', 'product', 'amount', 'note',
                  'handled_by', 'paid_at', 'student_phone']
        read_only_fields = ['enrollment', 'handled_by', 'paid_at']

    def validate(self, attrs):
        student_phone = attrs.pop('student_phone', None)
        session = attrs.get('session')
        product = attrs.get('product')

        if not session and not product:
            raise serializers.ValidationError(
                'Either session or product must be provided'
            )

        if student_phone:
            from users.models import Student
            try:
                student = Student.objects.get(phone=student_phone)
            except Student.DoesNotExist:
                raise serializers.ValidationError(
                    {'student_phone': 'No student found with this phone number'}
                )

            if session:
                source = session.source
                if not source:
                    raise serializers.ValidationError(
                        'Session has no attached schedule'
                    )
                from academics.models import Enrollment
                subject = source.subject
                enrollment, created = Enrollment.objects.get_or_create(
                    student=student,
                    subject=subject,
                    defaults={'handled_by': 'auto', 'paid': True}
                )
                if not created:
                    enrollment.paid = True
                    enrollment.save()
                attrs['enrollment'] = enrollment

        return attrs
