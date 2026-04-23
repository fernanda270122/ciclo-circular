import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_pitch_usuario'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AvisoUtil',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detalle', models.CharField(max_length=200)),
                ('descripcion', models.TextField()),
                ('contacto', models.CharField(max_length=30)),
                ('email', models.EmailField(max_length=254)),
                ('localidad', models.CharField(max_length=100)),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='avisos', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-creado'],
            },
        ),
    ]
