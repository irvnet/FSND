from datetime import datetime
from flask_wtf import FlaskForm as Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL, Length, Regexp, InputRequired
from wtforms import validators, ValidationError  
from models import GenresEnum
import re



state_choices=[
            ('AL', 'AL'),
            ('AK', 'AK'),
            ('AZ', 'AZ'),
            ('AR', 'AR'),
            ('CA', 'CA'),
            ('CO', 'CO'),
            ('CT', 'CT'),
            ('DE', 'DE'),
            ('DC', 'DC'),
            ('FL', 'FL'),
            ('GA', 'GA'),
            ('HI', 'HI'),
            ('ID', 'ID'),
            ('IL', 'IL'),
            ('IN', 'IN'),
            ('IA', 'IA'),
            ('KS', 'KS'),
            ('KY', 'KY'),
            ('LA', 'LA'),
            ('ME', 'ME'),
            ('MT', 'MT'),
            ('NE', 'NE'),
            ('NV', 'NV'),
            ('NH', 'NH'),
            ('NJ', 'NJ'),
            ('NM', 'NM'),
            ('NY', 'NY'),
            ('NC', 'NC'),
            ('ND', 'ND'),
            ('OH', 'OH'),
            ('OK', 'OK'),
            ('OR', 'OR'),
            ('MD', 'MD'),
            ('MA', 'MA'),
            ('MI', 'MI'),
            ('MN', 'MN'),
            ('MS', 'MS'),
            ('MO', 'MO'),
            ('PA', 'PA'),
            ('RI', 'RI'),
            ('SC', 'SC'),
            ('SD', 'SD'),
            ('TN', 'TN'),
            ('TX', 'TX'),
            ('UT', 'UT'),
            ('VT', 'VT'),
            ('VA', 'VA'),
            ('WA', 'WA'),
            ('WV', 'WV'),
            ('WI', 'WI'),
            ('WY', 'WY'),
]

genre_choices=[
            (GenresEnum.Alternative.name,    GenresEnum.Alternative.name),
            (GenresEnum.Blues.name,          GenresEnum.Blues.name),
            (GenresEnum.Classical.name,      GenresEnum.Classical.name),
            (GenresEnum.Electronic.name,     GenresEnum.Electronic.name),
            (GenresEnum.Folk.name,           GenresEnum.Folk.name),
            (GenresEnum.Funk.name,           GenresEnum.Funk.name),
            (GenresEnum.HipHop.name,         GenresEnum.HipHop.name),
            (GenresEnum.HeavyMetal.name,     GenresEnum.HeavyMetal.name),
            (GenresEnum.Instrumental.name,   GenresEnum.Instrumental.name),
            (GenresEnum.Jazz.name,           GenresEnum.Jazz.name),
            (GenresEnum.MusicalTheatre.name, GenresEnum.MusicalTheatre.name),
            (GenresEnum.Pop.name,            GenresEnum.Pop.name),
            (GenresEnum.Punk.name,           GenresEnum.Punk.name),
            (GenresEnum.RnB.name,            GenresEnum.RnB.name),
            (GenresEnum.Reggae.name,         GenresEnum.Reggae.name),
            (GenresEnum.RocknRoll.name,      GenresEnum.RocknRoll.name),
            (GenresEnum.Soul.name,           GenresEnum.Soul.name),
            (GenresEnum.Other.name,          GenresEnum.Other.name),
]


class ShowForm(Form):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

def is_valid_phone(number):
    """ Validate phone numbers like:
    1234567890 - no space
    123.456.7890 - dot separator
    123-456-7890 - dash separator
    123 456 7890 - space separator

    Patterns:
    000 = [0-9]{3}
    0000 = [0-9]{4}
    -.  = ?[-. ]

    Note: (? = optional) - Learn more: https://regex101.com/
    """
    regex = re.compile('^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$')
    return regex.match(number)

class VenueForm(Form):
    def validate(self):
      """Define a custom validate method in your Form:"""
      rv = Form.validate(self)
      if not rv:
          return False
      if not is_valid_phone(self.phone.data):
          self.phone.errors.append(':: Invalid phone number:')
          return False
      if not set(self.genres.data).issubset(dict(genre_choices).keys()):
          self.genres.errors.append(':: Invalid genres.')
          return False
      if self.state.data not in dict(state_choices).keys():
          self.state.errors.append(':: Invalid state.')
          return False
      # if pass validation
      return True

    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=state_choices
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )

    phone = StringField('phone')

    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=genre_choices
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    website_link = StringField(
        'website_link'
    )
    seeking_talent = BooleanField( 'seeking_talent' )
    seeking_description = StringField(
        'seeking_description'
    )






class ArtistForm(Form):

    def validate(self):
      """Define a custom validate method in your Form:"""
      rv = Form.validate(self)
      if not rv:
          return False
      if not is_valid_phone(self.phone.data):
          self.phone.errors.append(':: Invalid phone number:')
          return False
      if not set(self.genres.data).issubset(dict(genre_choices).keys()):
          self.genres.errors.append(':: Invalid genres.')
          return False
      if self.state.data not in dict(state_choices).keys():
          self.state.errors.append(':: Invalid state.')
          return False
      # if pass validation
      return True


    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=state_choices
    )
    phone = StringField('phone')
    
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=genre_choices
     )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
     )

    website_link = StringField(
        'website_link'
     )

    seeking_venue = BooleanField( 'seeking_venue' )

    seeking_description = StringField(
            'seeking_description'
     )

