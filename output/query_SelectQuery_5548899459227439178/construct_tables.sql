CREATE TABLE IF NOT EXISTS BGP_8188015215573083507 (product VARCHAR(255),
                                                            value1 VARCHAR(255),
                                                                   label VARCHAR(255),
                                                                         k_count INT);


DROP TABLE IF EXISTS delta_BGP_8188015215573083507;


CREATE TABLE IF NOT EXISTS delta_BGP_8188015215573083507 (product VARCHAR(255),
                                                                  value1 VARCHAR(255),
                                                                         label VARCHAR(255),
                                                                               k_count INT);


CREATE TABLE IF NOT EXISTS nu_BGP_8188015215573083507 (product VARCHAR(255),
                                                               value1 VARCHAR(255),
                                                                      label VARCHAR(255),
                                                                            k_count INT);


CREATE TABLE IF NOT EXISTS Filter_331046825976329928 (label VARCHAR(255),
                                                            product VARCHAR(255),
                                                                    value1 VARCHAR(255),
                                                                           k_count INT);


DROP TABLE IF EXISTS delta_Filter_331046825976329928;


CREATE TABLE IF NOT EXISTS delta_Filter_331046825976329928 (label VARCHAR(255),
                                                                  product VARCHAR(255),
                                                                          value1 VARCHAR(255),
                                                                                 k_count INT);


CREATE TABLE IF NOT EXISTS nu_Filter_331046825976329928 (label VARCHAR(255),
                                                               product VARCHAR(255),
                                                                       value1 VARCHAR(255),
                                                                              k_count INT);


CREATE TABLE IF NOT EXISTS Project_1055153065793086627 (label VARCHAR(255),
                                                              product VARCHAR(255),
                                                                      k_count INT);


DROP TABLE IF EXISTS delta_Project_1055153065793086627;


CREATE TABLE IF NOT EXISTS delta_Project_1055153065793086627 (label VARCHAR(255),
                                                                    product VARCHAR(255),
                                                                            k_count INT);


CREATE TABLE IF NOT EXISTS nu_Project_1055153065793086627 (label VARCHAR(255),
                                                                 product VARCHAR(255),
                                                                         k_count INT);


CREATE TABLE IF NOT EXISTS SelectQuery_5548899459227439178 (label VARCHAR(255),
                                                                  product VARCHAR(255),
                                                                          k_count INT);


DROP TABLE IF EXISTS delta_SelectQuery_5548899459227439178;


CREATE TABLE IF NOT EXISTS delta_SelectQuery_5548899459227439178 (label VARCHAR(255),
                                                                        product VARCHAR(255),
                                                                                k_count INT);


CREATE TABLE IF NOT EXISTS nu_SelectQuery_5548899459227439178 (label VARCHAR(255),
                                                                     product VARCHAR(255),
                                                                             k_count INT);