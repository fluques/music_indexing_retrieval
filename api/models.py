from django.db import models

# Create your models here.

class AudioFile(models.Model):
    file_field_name = models.FileField(upload_to='audio_files/')
    file_name = models.CharField(max_length=255)
    metadata = models.JSONField(blank=True, null=True,default=dict)
    embeddings = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name
    
class AudioSegmentRange(models.Model):
    audio_file = models.ForeignKey(AudioFile, on_delete=models.CASCADE)
    start_second = models.IntegerField()
    end_second = models.IntegerField()
