
class PostSelector:
    TITLE = 'h1[data-automation="job-detail-title"]'
    COMPANY_NAME = 'span[data-automation="advertiser-name"]'
    LOCATION = 'span[data-automation="job-detail-location"]'
    WORK_TYPE = 'span[data-automation="job-detail-work-type"]'
    DETAIL_SALARY = 'span[data-automation="job-detail-salary"]'
    EXPECTED_SALARY = 'span[data-automation="job-detail-add-expected-salary"]'
    ### _1oozmqe0 l218ib5b l218ibhf l218ib6z
    ### div._1oozmqe0.l218ib5b.l218ibhf.l218ib6z span._1oozmqe0.l218ib4z._1ljn1h70._1ljn1h71._1ljn1h71u._1ljn1h76._1kdtdvw4
    ### div._1oozmqe0.l218ib5b.l218ibhf.l218ib73 div._1oozmqe0.l218ib5b.l218ibhf.l218ib6z span._1oozmqe0.l218ib4z._1ljn1h70._1ljn1h71._1ljn1h71u._1ljn1h76._1kdtdvw4
    POST_DATE = 'span._1oozmqe0.l218ib4z._1ljn1h70._1ljn1h71._1ljn1h71u._1ljn1h76._1kdtdvw4'
    DESCRIPTION = 'div[data-automation="jobAdDetails"]'


class ListSelector:
    JOB = 'a[data-automation="jobTitle"]'
    NEXT_PAGE_BTN = 'li._1oozmqe0.l218ibbb.l218ibb0.l218ibx a'  # Next page button selector
    JOB_NUMBER_COUNT_A = 'div[data-automation="totalJobsCountBcues"] span'
    JOB_NUMBER_COUNT_B = 'span[data-automation="totalJobsCount"]'
