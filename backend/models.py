class Company:
    fields = set([
        'id',
        'overview_url',
        'reviews_url',
        'linkedin_url',
        # From Glassdoor.
        'name',
        'rating',
        'review_counts',
        'website',
        'headquarters',
        'part_of',
        'size',
        'founded',
        'type',
        'industry',
        'revenue',
        'competitors',
        'logo_url',
    ])

    def __init__(self, id):
        self.dict = {}
        self.dict['id'] = id

    def update_data(self, data={}):
        for k, v in data.items():
            field_name = k.replace(' ', '_').lower()
            if field_name not in self.fields:
                id = self.dict.get('id')
                print(f'[WARN] Unexpected key "{k}" when updating "{id}".')
            self.dict[field_name] = v

    def __getitem__(self, key):
        return self.dict.__getitem__(key)

    def __setitem__(self, key, value):
        return self.dict.__setitem__(key, value)

    @property
    def missing_fields(self):
        pass

    def __str__(self):
        return self.dict.__str__()


class FailedCompanyError():
    def __init__(self, company_name, exception):
        self.company_name = company_name
        self.exception = exception

    def __str__(self):
        return self.exception.__str__()
