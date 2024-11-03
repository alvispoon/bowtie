
#1a. Obtain the number of submitted claims in the year 2021 by products.
select p.product, count(c.id) as num_claim from claim c, policy p 
where c.policy_number = p.policy_number
and extract(year from CAST(submit_date as timestamp)) = 2021
group by p.product
order by count(c.id) desc

#***REMARKS****
#In case you want to exclude all CANCELLED / WITHDRAWN claim
#and LOWER(status) NOT IN ('withdrawn', 'canceled')
#***REMARKS****

#1b. Compare the average net premium received from new policies vs returning
#policies (i.e. the 2nd+ policy of the same user)

#Assumption- Only 2021 
#Assume 'shortfall' case is excception and excluded

select case when policy_rank = 1 then 'NEW' else 'RETURNING' END as policy_type, 
avg(totalrev) as avg_rev
from (
select p.policy_number, p.user_id, 
SUM(
    CASE 
        WHEN i.status = 'refund' THEN -1 * i.total_amount  --REFUND LOGIC
        ELSE i.total_amount 
    END
) as net_revenue
, ROW_NUMBER() OVER (PARTITION BY p.user_id order by p.issue_date) as policy_rank
from policy p, invoice i
where p.policy_number = i.policy_number
and i.status = 'paid'                   
and i.invoice_type != 'shortfall'      --Exclude ShortFall Case
and extract(year from CAST(charge_date as timestamp)) = 2021 --2021 DATA ONLY
) a


