import base64
from email.mime.nonmultipart import MIMENonMultipart
from email.mime.image import MIMEImage

from django.test import TestCase

from django_better_azure_communication_email import attachment


class TestGetConverter(TestCase):
    """attachment.get_converter()"""

    def test_getting_mime_base_converter(self):
        msg = MIMENonMultipart('application', 'http')
        converter = attachment.get_converter(msg)
        self.assertIsInstance(converter, attachment.MIMEBaseConverter)

    def test_getting_tuple_base_converter(self):
        att_file = ('file.txt', 'file content', 'text/plain')
        converter = attachment.get_converter(att_file)
        self.assertIsInstance(converter, attachment.TupleBaseConverter)

    def test_unknown_attachment_type(self):
        att_file = object()
        with self.assertRaises(TypeError):
            attachment.get_converter(att_file)  # type: ignore


class TestTupleBaseConverter(TestCase):
    """attachment.TupleBaseConverter()"""

    def test_plain_text_content(self):
        att_file = ('file.txt', 'file content', 'text/plain')
        converter = attachment.TupleBaseConverter(att_file)

        self.assertEqual(converter.get_filename(), att_file[0])
        self.assertEqual(converter.get_filetype(), att_file[2])
        self.assertEqual(
            converter.get_content(),
            base64.b64encode(att_file[1].encode()).decode(),
        )

    def test_bytes_content(self):
        att_file = ('file.txt', b'file content', 'application/octet-stream')
        converter = attachment.TupleBaseConverter(att_file)

        self.assertEqual(converter.get_filename(), att_file[0])
        self.assertEqual(converter.get_filetype(), att_file[2])
        self.assertEqual(
            converter.get_content(),
            base64.b64encode(att_file[1]).decode(),
        )


class TestMimeBaseConverter(TestCase):
    """attachment.MIMEBaseConverter()"""

    def test_bytes_content(self):
        payload = b'file content'
        filename = 'file.txt'
        filetype = 'application/octet-stream'

        msg = MIMENonMultipart(*filetype.split('/'))
        msg['Content-Disposition'] = f'attachment; filename="{filename}"'
        msg.set_payload(payload)

        converter = attachment.MIMEBaseConverter(msg)

        self.assertEqual(converter.get_filename(), filename)
        self.assertEqual(converter.get_filetype(), filetype)
        self.assertEqual(
            converter.get_content(),
            base64.b64encode(payload).decode(),
        )

    def test_bytes_b64encoded_content(self):
        payload = base64.b64encode(b'file content')
        filetype = 'application/octet-stream'

        msg = MIMENonMultipart(*filetype.split('/'))
        msg['Content-Disposition'] = f'attachment;'
        msg['Content-Transfer-Encoding'] = 'base64'
        msg.set_payload(payload)

        converter = attachment.MIMEBaseConverter(msg)

        self.assertEqual(converter.get_filename(), 'untitled')
        self.assertEqual(converter.get_filetype(), filetype)
        self.assertEqual(converter.get_content(), payload.decode())

    def test_inline_image_content(self):
        payload= (
            b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A"
            b"\x00\x00\x00\x0D\x49\x48\x44\x52"
            b"\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x06\x00\x00\x00\x1F\x15\xC4"
            b"\x89\x00\x00\x00\x0A\x49\x44\x41"
            b"\x54\x78\x9C\x63\x60\x00\x00\x00"
            b"\x02\x00\x01\xE5\x27\xD4\x0D\x00"
            b"\x00\x00\x00\x49\x45\x4E\x44\xAE"
            b"\x42\x60\x82"
        )
        msg = MIMEImage(payload, _subtype="png")
        msg.add_header("Content-ID", "file")
        msg.add_header("Content-Disposition", "inline", filename="file.png")

        converter = attachment.MIMEBaseConverter(msg)

        self.assertEqual(converter.get_filename(), 'file.png')
        self.assertEqual(converter.get_filetype(), 'image/png')
        self.assertEqual(converter.get_content_id(), 'file')