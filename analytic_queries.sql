
/*
create temp tables. 
Ideally we will need a logical/physical datawarehouse, which requires its own ETL/ELT schema
*/
drop table if exists dim_company;
create temp table dim_company as
select distinct
	company_id, name, company_type, state, referral_code, job_count, cast(created_at as timestamp) created_at
from company;

drop table if exists dim_contacts;
create temp table dim_contacts as
select distinct
	user_id, value as user_name, contact_id, is_primary
from contacts;
	
drop table if exists dim_portfolio;
create temp table dim_portfolio as
select distinct 
	portfolio_id, pm_id, pm_company_id, max_cost_soft, max_cost_hard, property_count
from portfolio;

drop table if exists dim_property;
create temp table dim_property as
select distinct 
	portfolio_id, property_id, is_active, state, pm_id
from property;

drop table if exists dim_settings;
create temp table dim_settings as
select distinct
	pm_company_id, send_invoice
from settings
---End of temp tables

/*
	--- Analytic queries
*/
--count of actual properties of customers, by region
select dc.name, dp.state, count(*) as total_properties
from dim_company dc
	inner join dim_portfolio dpo
		on dc.company_id = dpo.pm_company_id
	inner join dim_property dp
		on dpo.portfolio_id = dp.portfolio_id
group by dc.name, dp.state

--Invoice based Customers
select dc.company_id, dc.name
from dim_company dc
where exists 
	(
		select * from dim_settings ds
		where dc.company_id = ds.pm_company_id
	)

--new customers this year, with property counts
select dc.name, count(*) as total_properties
from dim_company dc
	inner join dim_portfolio dpo
		on dc.company_id = dpo.pm_company_id
	inner join dim_property dp
		on dpo.portfolio_id = dp.portfolio_id
where extract(year from dc.created_at) = extract(year from now())
and not exists
	(
		select 1
		from dim_company dc_in
		where extract(year from dc.created_at) < extract(year from now())
		and dc.company_id = dc_in.company_id
	)
group by dc.name

-- great jones managed asset value

