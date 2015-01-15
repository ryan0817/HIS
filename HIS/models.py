from django.db import models

class Issue(models.Model):
    issue_key = models.CharField(max_length=5)
    issue_value = models.CharField(max_length=20)
    def __unicode__(self):
        return u'%s' % self.issue_value

class Source(models.Model):
    source_key = models.CharField(max_length=10)
    source_value = models.CharField(max_length=20)
    def __unicode__(self):
        return u'%s,%s' % (self.source_key,self.source_value)

class SickRecord(models.Model):
    name = models.CharField(max_length=30,blank=True)
    birthday = models.DateField(blank=True, null=True)
    pid = models.CharField(max_length=20,blank=True)
    sex = models.CharField(max_length=10,blank=True)
    sick_id = models.CharField(max_length=50,blank=True)
    sick_receive_date = models.DateField(blank=True, null=True)
    source = models.ForeignKey(Source)
    sick_result = models.CharField(max_length=20,blank=True)
    care_dt = models.CharField(max_length=5,blank=True)
    care_check = models.CharField(max_length=5, blank=True)
    issues = models.ManyToManyField(Issue,blank=True)
    care_content = models.CharField(max_length=1000,blank=True)
    care_date = models.DateField(blank=True, null=True)
    def __unicode__(self):
        return u'%s %s' % (self.sick_id, self.name)



