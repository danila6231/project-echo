from app.infrastructure.instagram_client import InstagramApiClient

CODE = 'AQBWBEKtWMMz080avnPM2zixnfpImGXIZr5D7HkDzMXLsr0YQ6ejhHbgM2d20FbUYwlG9AzQOd0YHTTSp_hEfuhsjgcF73IBYxYD2615ZGisry7YhJ-DXLekrY0Mr6pmdhXe95fk79rnaDYmn3AmqYmBmbc8bkLZPvp3XH9_nPXbm7_GwpU5O6uTN0TgtCUmsMXcNzfDhvkx-Fa75TLJymSGskNqF7xHYADtprylo0vQBQ'

SHORT_LIVED_TOKEN = 'IGAAIJkphRBX5BZAE1HeWN3bmUtUWRBVVRKTGJqVlVZAREZALYlBYNWJockZAfcElDQ3lmWVhKWlZAWM2FCTzZA1ZA0MzX1R4VmdWTG11RGtTYUFEMm1xbzJMLWRuVXlGUDRBVUtNN0ZAOQXlTSkNUYXdIUXQ4bE1FQmJDUGtXVnktcFdGSjUtV2dKMXI1THpfQTEtNDhfeXRpRgZDZD'
LONG_LIVED_TOKEN = 'IGAAIJkphRBX5BZAE5FaGNSejhRaWRJZAU14QmRXZAGVMN0stSkNIV1hIQktqZAEQ1enRDNlFiQ0dfbWN6cnVvaklKdmhhX0NqZAFpOd3FrVEtNQlRhclpiSXlBMVNWY1RoZA194VzhGdmU5LVF0VzMzVWZAmbmxR'
USER_ID = 0

if __name__ == "__main__":
    api = InstagramApiClient()
    api.short_lived_token = SHORT_LIVED_TOKEN
    api.long_lived_token = LONG_LIVED_TOKEN
    allPosts = api.posts()
    print(api.comments(allPosts.data[0].id))

    # api.short_lived_token = SHORT_LIVED_TOKEN
    # api.long_lived_token = LONG_LIVED_TOKEN
    #
    # allPosts = api.posts()
    # print(api.comments(allPosts.data[0].id))

    # api.short_lived_token = SHORT_LIVED_TOKEN
    # api.long_lived_token = LONG_LIVED_TOKEN
    #
    # print(api.get_user_info())
