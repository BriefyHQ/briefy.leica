"""Parser for internal comment."""
from briefy.common.db import datetime_utcnow
from briefy.common.users import SystemUser
from datetime import datetime
from datetime import timezone
from uuid import uuid4

import re


breaker = '\n------------------------------\n'
import_replace = breaker + 'CREATED_AT Imported using a script' + breaker
script_replace = breaker + r'\1 Imported using a script' + breaker
date_2016_replace = breaker + r'2016-\2-\1T00:00:00.00+00:00 \3'
date_2016_md_replace = breaker + r'2016-\1-\2T00:00:00.00+00:00 \3'
date_2017_replace = breaker + r'2017-\2-\1T00:00:00.00+00:00 \3'
date_2017_md_replace = breaker + r'2017-\1-\2T00:00:00.00+00:00 \3'

DATE_PATTERN = r'^((\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})\.?[\d]*\+00:00)'

DATE_PATTERNS = [
    ('^(\d{1,2})\ (May|Jun|Jul|Aug|Agu|Sep|Oct|Nov|Dec)\ 2016(.*)', date_2016_replace),
    ('\n(\d{1,2})\ (May|Jun|Jul|Aug|Agu|Sep|Oct|Nov|Dec)\ 2016(.*)', date_2016_replace),
    ('^(\d{1,2})\ (Jan|Feb)\ 2017(.*)', date_2017_replace),
    ('\n(\d{1,2})\ (Jan|Feb)\ 2017(.*)', date_2017_replace),
    ('^(Jan|Feb)[\., ]?(\d{1,2})\ ?(.*)', date_2017_md_replace),
    ('\n(Jan|Feb)[\., ]?(\d{1,2})\ ?(.*)', date_2017_md_replace),
    ('^(\d{1,2})th of (Jan)uary\ ?(.*)', date_2017_replace),
    ('\n(\d{1,2})th of (Jan)uary\ ?(.*)', date_2017_replace),
    ('^(\d{1,2})[\., ]{0,2}(Jan|Feb)\ ?(.*)', date_2017_replace),
    ('\n(\d{1,2})[\., ]{0,2}(Jan|Feb)\ ?(.*)', date_2017_replace),
    ('^(Mar|Apr|May|Jun|Jul|Aug|Agu|Sep|Oct|Nov|Dec)[\., ]?(\d{1,2})\ ?(.*)', date_2016_md_replace),
    (
        '\n(Mar|Apr|May|Jun|Jul|Aug|Agu|Sep|Oct|Nov|Dec)[\., ]?(\d{1,2})\ ?(.*)',
        date_2016_md_replace
    ),
    (
        '^(\d{1,2})[\., ]{0,2}(Mar|Apr|May|Jun|Jul|Aug|Agu|Sep|Oct|Nov|Dec)\ ?(.*)',
        date_2016_replace
    ),
    (
        '\n(\d{1,2})[\., ]{0,2}(Mar|Apr|May|Jun|Jul|Aug|Agu|Sep|Oct|Nov|Dec)\ ?(.*)',
        date_2016_replace
    ),
    ('^(\d{1,2})[\.,\/](0[6-9]{1}|1[0,1,2]) ?(.*)', date_2016_replace),
    ('\n(\d{1,2})[\.,\/](0[6-9]{1}|1[0,1,2]) ?(.*)', date_2016_replace),
    ('^(\d{1,2})[\.,\/](0?[1-2]{1}) ?(.*)', date_2017_replace),
    ('\n(\d{1,2})[\.,\/](0?[1-2]{1}) ?(.*)', date_2017_replace),
    ('^((\d{4})[-,.](\d{1,2})[-,.](\d{1,2}))[^T](.*)', breaker + r'\2-\3-\4T00:00:00.00+00:00 \5'),
    ('-(Jan|1)-', '-01-'),
    ('-(Feb|2)-', '-02-'),
    ('-(Mar|3)-', '-03-'),
    ('-(Apr|4)-', '-04-'),
    ('-(May|5)-', '-05-'),
    ('-(Jun|6)-', '-06-'),
    ('-(Jul|7)-', '-07-'),
    ('-(Aug|Agu|8)-', '-08-'),
    ('-(Sep|9)-', '-09-'),
    ('-(Oct|10)-', '-10-'),
    ('-(Nov|11)-', '-11-'),
    ('-(Dec|12)-', '-12-'),
    ('-(\d)T', r'-0\1T'),
    ('\+00:00 [-,:]', '+00:00 '),
]

BASE_PATTERNS = [
    ('\n([-]+)\n', breaker),
    ('^([-]+)\n', breaker),
]

INTERNAL_PATTERNS = BASE_PATTERNS + [
    (
        '\nTO ([^:]*): (AR|Ariana|GF|Christian|Flora|francesca|Nayeon)[/, ,:]*(.*)',
        breaker + r'\2 [\1]'
    ),
    (
        '^TO ([^:]*): (AR|Ariana|GF|Christian|Flora|francesca|Nayeon)[/, ,:]*(.*)',
        breaker + r'\2 [\1]'
    ),
    ('\n(AR|Ariana|GF|Christian|Flora|francesca|Nayeon)[/, ,:]*(.*)', breaker + r'\2 [\1]'),
    ('^(AR|Ariana|GF|Christian|Flora|francesca|Nayeon)[/, ,:]*(.*)', breaker + r'\2 [\1]'),
    ('\n(Cancelled using a script)\n?', breaker + r'\1' + breaker),
    ('^(Cancelled using a script)\n?', breaker + r'\1' + breaker),
    ('\n(Imported using a script)\n?', import_replace),
    ('^(Imported using a script)\n?', import_replace),
    ('\n?(([^\n]+) - Imported using a script)\n?', script_replace),
    ('\nJob imported from spreadsheet data\n?', import_replace),
    ('^Job imported from spreadsheet data\n?', import_replace),
    ('\((AR|Ariana|GF|Christian|Flora|francesca|Nayeon)\)', r'[\1]'),
    ('^QA (.*)', r'\1 [QA]'),
] + DATE_PATTERNS


PATTERNS = BASE_PATTERNS + DATE_PATTERNS


def comment_format_first_line(created_at: datetime = None, body: str='') -> tuple:
    """Parse and format the body to extract date from first line."""
    created_at = datetime_utcnow() if not created_at else created_at
    first_line = body.split('\n')[0]
    new_first_line = first_line
    matches = re.findall(DATE_PATTERN, new_first_line)
    if not matches:
        for pattern, replacer in DATE_PATTERNS:
            new_first_line = re.sub(pattern, replacer, new_first_line)
            new_first_line = new_first_line.replace('\n------------------------------\n', '')
        # Replace orphan time
        new_first_line = new_first_line.replace(' T00:00:00.00+00:00', '')
        matches = re.findall(DATE_PATTERN, new_first_line)
    if matches:
        try:
            created_at = datetime(*[int(i) for i in matches[0][1:-1]], tzinfo=timezone.utc)
        except:
            # Deal with error trying to convert wrong dates (ie 34 Jan)
            created_at = datetime_utcnow()
        new_first_line = re.sub(DATE_PATTERN, '', new_first_line)
        body = body.replace(first_line, new_first_line).strip()
    return created_at, body


def parse_internal_comments(obj, kobj):
    """Parse comment field and return a list of comments."""
    comments = []
    input_date = kobj.input_date
    created_at = input_date.isoformat() if input_date else ''
    src_comment = kobj.internal_comments
    for pattern, replacer in INTERNAL_PATTERNS:
        src_comment = re.sub(pattern, replacer, src_comment)
        src_comment = src_comment.replace('CREATED_AT', created_at)
    contents = src_comment.split('------------------------------\n')
    contents = [c.strip() for c in contents if c.strip()]
    contents.reverse()
    author = obj.project.project_manager if obj.project.project_manager else SystemUser.id
    author_role = 'project_manager'
    for body in contents:
        created_at, body = comment_format_first_line(datetime_utcnow(), body)
        if 'using a script' in body:
            author = SystemUser.id
            author_role = 'system'
        comments.append(
            dict(
                id=uuid4(),
                entity_id=obj.id,
                entity_type=obj.__class__.__name__,
                author_id=author,
                content=body,
                created_at=created_at,
                updated_at=created_at,
                author_role=author_role,
                to_role='briefy',
                internal=True,
            )
        )
    return comments
