# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Recipient'
        db.create_table(u'discussions_recipient', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('discussion', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['discussions.Discussion'])),
            ('folder', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='recipients', null=True, to=orm['discussions.Folder'])),
            ('read_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('deleted_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=1, db_index=True)),
        ))
        db.send_create_signal('discussions', ['Recipient'])

        # Adding model 'Discussion'
        db.create_table('discussions_discussion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(related_name='discussions_sent', to=orm['auth.User'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('sender_deleted_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('latest_message', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='latest_discussions', null=True, to=orm['discussions.Message'])),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=140)),
            ('date_sent', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_update', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('discussions', ['Discussion'])

        # Adding model 'Message'
        db.create_table('discussions_discussionmessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sent_messages', to=orm['auth.User'])),
            ('discussion', self.gf('django.db.models.fields.related.ForeignKey')(related_name='messages', to=orm['discussions.Discussion'])),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('sent_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('sender_deleted_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('message_content', self.gf('django.db.models.fields.TextField')()),
            ('date_sent', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('discussions', ['Message'])

        # Adding M2M table for field files on 'Message'
        m2m_table_name = db.shorten_name('discussions_discussionmessage_files')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('message', models.ForeignKey(orm['discussions.message'], null=False)),
            ('staticfile', models.ForeignKey(orm['ulule_base.staticfile'], null=False))
        ))
        db.create_unique(m2m_table_name, ['message_id', 'staticfile_id'])

        # Adding model 'Folder'
        db.create_table(u'discussions_folder', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('discussions', ['Folder'])


    def backwards(self, orm):
        # Deleting model 'Recipient'
        db.delete_table(u'discussions_recipient')

        # Deleting model 'Discussion'
        db.delete_table('discussions_discussion')

        # Deleting model 'Message'
        db.delete_table('discussions_discussionmessage')

        # Removing M2M table for field files on 'Message'
        db.delete_table(db.shorten_name('discussions_discussionmessage_files'))

        # Deleting model 'Folder'
        db.delete_table(u'discussions_folder')


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
            'username': ('sluggable.fields.SluggableField', [], {'unique': 'True', 'max_length': '50', 'populate_from': 'None'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'discussions.discussion': {
            'Meta': {'object_name': 'Discussion'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_sent': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latest_message': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'latest_discussions'", 'null': 'True', 'to': "orm['discussions.Message']"}),
            'recipients': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'discussions_received'", 'symmetrical': 'False', 'through': "orm['discussions.Recipient']", 'to': u"orm['auth.User']"}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'discussions_sent'", 'to': u"orm['auth.User']"}),
            'sender_deleted_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '140'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'discussions.folder': {
            'Meta': {'ordering': "['-created_at']", 'object_name': 'Folder'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        'discussions.message': {
            'Meta': {'object_name': 'Message', 'db_table': "'discussions_discussionmessage'"},
            'body': ('django.db.models.fields.TextField', [], {}),
            'date_sent': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'discussion': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'messages'", 'to': "orm['discussions.Discussion']"}),
            'files': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ulule_base.StaticFile']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message_content': ('django.db.models.fields.TextField', [], {}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sent_messages'", 'to': u"orm['auth.User']"}),
            'sender_deleted_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'sent_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'discussions.recipient': {
            'Meta': {'object_name': 'Recipient'},
            'deleted_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'discussion': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['discussions.Discussion']"}),
            'folder': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'recipients'", 'null': 'True', 'to': "orm['discussions.Folder']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'read_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        'ulule_base.staticfile': {
            'Meta': {'object_name': 'StaticFile'},
            'file': ('ulule_base.fields.ContentTypeRestrictedFileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['discussions']