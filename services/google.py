import gspread


class Google:
    
    @staticmethod
    def get_data_from_google_sheet():
        gc = gspread.service_account(filename='tg-bot-token.json')
        sht_token = '1h3sMe3X4h4IAHVHCh84KsrNSS3Bp7B2yNsGRJ8_3XlI'
        sht = gc.open_by_key(sht_token)
        worksheet = sht.get_worksheet(0)
        list_of_lists = worksheet.get_all_records()
        print(list_of_lists)
    
    @staticmethod
    def update_sht():
        gc = gspread.service_account(filename='tg-bot-token.json')
        sht_token = '1h3sMe3X4h4IAHVHCh84KsrNSS3Bp7B2yNsGRJ8_3XlI'
        sht = gc.open_by_key(sht_token)
        worksheet = sht.get_worksheet(0)
        
        tset_data = [
            ["CMBaff", "CR", 50, "17:00", "01:00", "gmt + 3"],
            ["CMBaff", "MX", 50, "17:00", "01:00", "gmt + 3"],
            ["CMBaff", "IT", 40, "11:00", "19:00", "gmt + 3"],
            ["CMBaff", "GR", 40, "11:00", "19:00", "gmt + 3"],
        ]

        for row in tset_data:
            worksheet.append_row(row)
