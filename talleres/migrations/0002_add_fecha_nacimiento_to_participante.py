from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('talleres', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='participante',
            name='fecha_nacimiento',
            field=models.DateField(blank=True, help_text='Fecha de nacimiento del participante', null=True, verbose_name='Fecha de nacimiento'),
        ),
    ]
