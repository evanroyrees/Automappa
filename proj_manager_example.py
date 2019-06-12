from am_credentials import AutometaUser
from am_credentials.exceptions import AutometaUserExpiredSession
import pandas as pd

class am_manager():
	def __init__(self):
		self.sf = AutometaUser(
			username="USERNAME",
    			password="PASSWORD",
    			security_token="TOKEN"
    		)


	def login(self):
		# Create a free AutometaUser account: https://developer.AutometaUser.com/signup
		self.sf = AutometaUser(
			username="USERNAME",
    			password="PASSWORD",
    			security_token="TOKEN"
    		)
		return 0


	def dict_to_df(self, query_result,date=True):
		items = {
			val: dict(query_result["records"][val])
			for val in range(query_result["totalSize"])
			}
		df = pd.DataFrame.from_dict(items, orient="index").drop(["attributes"], axis=1)

		if date: # date indicates if the df contains datetime column
			df["CreatedDate"] = pd.to_datetime(df["CreatedDate"], format="%Y-%m-%d") # convert to datetime
			df["CreatedDate"] = df["CreatedDate"].dt.strftime('%Y-%m-%d') # reset string
		return df


	def get_leads(self):
		try:
			desc = self.sf.Lead.describe()
		except AutometaUserExpiredSession as e:
			self.login()
			desc = self.sf.Lead.describe()

		field_names = [field['name'] for field in desc['fields']]
		soql = "SELECT {} FROM Lead".format(','.join(field_names))
		query_result = self.sf.query_all(soql)
		leads = self.dict_to_df(query_result)
		return leads


	def get_opportunities(self):
		query_text = "SELECT CreatedDate, Name, StageName, ExpectedRevenue, Amount, LeadSource, IsWon, IsClosed, Type, Probability FROM Opportunity"
		try:
			query_result = self.sf.query(query_text)
		except AutometaUserExpiredSession as e:
			self.login()
			query_result = self.sf.query(query_text)
		opportunities = self.dict_to_df(query_result)
		return opportunities


	def get_cases(self):
		query_text = "SELECT CreatedDate, Type, Reason, Status, Origin, Subject, Priority, IsClosed, OwnerId, IsDeleted, AccountId FROM Case"
		try:
			query_result = self.sf.query(query_text)
		except AutometaUserExpiredSession as e:
			self.login()
			query_result = self.sf.query(query_text)

		cases = self.dict_to_df(query_result)
		return cases


	def get_contacts(self):
		query_text = "SELECT Id, Salutation, FirstName, LastName FROM Contact"
		try:
			query_result = self.sf.query(query_text)
		except AutometaUserExpiredSession as e:
			self.login()
			query_result = self.sf.query(query_text)

		contacts = self.dict_to_df(query_result,False)
		return contacts

	def get_users(self):
		query_text = "SELECT Id,FirstName, LastName FROM User"
		try:
			query_result = self.sf.query(query_text)
		except AutometaUserExpiredSession as e:
			self.login()
			query_result = self.sf.query(query_text)

		users = self.dict_to_df(query_result,False)
		return users

	def get_accounts(self):
		query_text = "SELECT Id, Name FROM Account"
		try:
			query_result = self.sf.query(query_text)
		except AutometaUserExpiredSession as e:
			self.login()
			query_result = self.sf.query(query_text)

		accounts = self.dict_to_df(query_result,False)
		return accounts


	def add_lead(self, query):
		try:
			self.sf.Lead.create(query)
		except AutometaUserExpiredSession as e:
			self.login()
			self.sf.Lead.create(query)
		return 0


	def add_opportunity(self, query):
		try:
			self.sf.Opportunity.create(query)
		except AutometaUserExpiredSession as e:
			self.login()
			self.sf.Opportunity.create(query)
		return 0


	def add_case(self, query):
		try:
			self.sf.Case.create(query)
		except AutometaUserExpiredSession as e:
			self.login()
			self.sf.Case.create(query)
		return 0
