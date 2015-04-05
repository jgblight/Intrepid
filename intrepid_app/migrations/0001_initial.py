# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Location'
        db.create_table(u'intrepid_app_location', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('lat', self.gf('django.db.models.fields.FloatField')()),
            ('lon', self.gf('django.db.models.fields.FloatField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'intrepid_app', ['Location'])

        # Adding model 'Profile'
        db.create_table(u'intrepid_app_profile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('image_file', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('image_x', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('image_y', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('hometown', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['intrepid_app.Location'], null=True, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'intrepid_app', ['Profile'])

        # Adding model 'Trip'
        db.create_table(u'intrepid_app_trip', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('image_file', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('image_x', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('image_y', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('image_width', self.gf('django.db.models.fields.FloatField')(default=1)),
            ('text', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'intrepid_app', ['Trip'])

        # Adding model 'Pin'
        db.create_table(u'intrepid_app_pin', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('trip', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['intrepid_app.Trip'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('pin_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2015, 4, 5, 0, 0))),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['intrepid_app.Location'])),
            ('tracks', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'intrepid_app', ['Pin'])

        # Adding model 'Media'
        db.create_table(u'intrepid_app_media', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pin', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['intrepid_app.Pin'], null=True, blank=True)),
            ('caption', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
        ))
        db.send_create_signal(u'intrepid_app', ['Media'])

        # Adding model 'Image'
        db.create_table(u'intrepid_app_image', (
            (u'media_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['intrepid_app.Media'], unique=True, primary_key=True)),
            ('media', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
        ))
        db.send_create_signal(u'intrepid_app', ['Image'])


    def backwards(self, orm):
        # Deleting model 'Location'
        db.delete_table(u'intrepid_app_location')

        # Deleting model 'Profile'
        db.delete_table(u'intrepid_app_profile')

        # Deleting model 'Trip'
        db.delete_table(u'intrepid_app_trip')

        # Deleting model 'Pin'
        db.delete_table(u'intrepid_app_pin')

        # Deleting model 'Media'
        db.delete_table(u'intrepid_app_media')

        # Deleting model 'Image'
        db.delete_table(u'intrepid_app_image')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'intrepid_app.image': {
            'Meta': {'object_name': 'Image', '_ormbases': [u'intrepid_app.Media']},
            'media': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            u'media_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['intrepid_app.Media']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'intrepid_app.location': {
            'Meta': {'object_name': 'Location'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {}),
            'lon': ('django.db.models.fields.FloatField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'intrepid_app.media': {
            'Meta': {'object_name': 'Media'},
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pin': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['intrepid_app.Pin']", 'null': 'True', 'blank': 'True'})
        },
        u'intrepid_app.pin': {
            'Meta': {'object_name': 'Pin'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['intrepid_app.Location']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'pin_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 4, 5, 0, 0)'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'tracks': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'trip': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['intrepid_app.Trip']"})
        },
        u'intrepid_app.profile': {
            'Meta': {'object_name': 'Profile'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'hometown': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['intrepid_app.Location']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_file': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'image_x': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'image_y': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'intrepid_app.trip': {
            'Meta': {'object_name': 'Trip'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_file': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'image_width': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            'image_x': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'image_y': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['intrepid_app']