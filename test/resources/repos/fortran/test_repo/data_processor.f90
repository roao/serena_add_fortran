! Data processing module with advanced features
module data_processor
    use math_operations
    implicit none
    
    private
    public :: process_data, data_filter, analysis_type
    
    ! Enumeration-like parameters
    integer, parameter :: FILTER_LOWPASS = 1
    integer, parameter :: FILTER_HIGHPASS = 2
    integer, parameter :: FILTER_BANDPASS = 3
    
    ! Abstract interface
    abstract interface
        function filter_function(x) result(y)
            real(kind=8), intent(in) :: x
            real(kind=8) :: y
        end function filter_function
    end interface
    
    ! Derived type for analysis configuration
    type :: analysis_type
        integer :: method
        real(kind=8) :: threshold
        logical :: normalize
        procedure(filter_function), pointer, nopass :: filter => null()
    end type analysis_type
    
contains
    
    ! Main data processing subroutine
    subroutine process_data(data_array, n, result)
        implicit none
        integer, intent(in) :: n
        real(kind=8), intent(inout) :: data_array(n)
        real(kind=8), intent(out) :: result
        
        ! Local variables
        real(kind=8) :: mean_val, std_val
        integer :: i
        logical :: converged
        
        ! Process data using internal procedures
        call remove_outliers()
        call smooth_data()
        
        ! Calculate final result
        call calculate_stats(data_array, n, mean_val, std_val)
        result = mean_val + 2.0_8 * std_val
        
    contains
        ! Internal procedure: remove outliers
        subroutine remove_outliers()
            implicit none
            real(kind=8) :: mean_temp, std_temp
            integer :: j
            
            call calculate_stats(data_array, n, mean_temp, std_temp)
            do j = 1, n
                if (abs(data_array(j) - mean_temp) > 3.0_8 * std_temp) then
                    data_array(j) = mean_temp
                end if
            end do
        end subroutine remove_outliers
        
        ! Internal procedure: smooth data
        subroutine smooth_data()
            implicit none
            real(kind=8) :: smoothed(n)
            integer :: j
            
            do j = 2, n-1
                smoothed(j) = (data_array(j-1) + data_array(j) + data_array(j+1)) / 3.0_8
            end do
            smoothed(1) = data_array(1)
            smoothed(n) = data_array(n)
            data_array = smoothed
        end subroutine smooth_data
        
    end subroutine process_data
    
    ! Generic data filter subroutine
    subroutine data_filter(data_in, n, data_out, config)
        implicit none
        integer, intent(in) :: n
        real(kind=8), intent(in) :: data_in(n)
        real(kind=8), intent(out) :: data_out(n)
        type(analysis_type), intent(in) :: config
        
        integer :: i
        
        ! Apply filtering based on configuration
        do i = 1, n
            select case (config%method)
                case (FILTER_LOWPASS)
                    data_out(i) = apply_lowpass(data_in(i), config%threshold)
                case (FILTER_HIGHPASS)
                    data_out(i) = apply_highpass(data_in(i), config%threshold)
                case (FILTER_BANDPASS)
                    data_out(i) = apply_bandpass(data_in(i), config%threshold)
                case default
                    data_out(i) = data_in(i)
            end select
        end do
        
        ! Normalize if requested
        if (config%normalize) then
            call normalize_array(data_out, n)
        end if
        
    end subroutine data_filter
    
    ! Simple low-pass filter implementation
    function apply_lowpass(input, cutoff) result(output)
        implicit none
        real(kind=8), intent(in) :: input, cutoff
        real(kind=8) :: output
        
        output = input * exp(-cutoff)
    end function apply_lowpass
    
    ! Simple high-pass filter implementation
    function apply_highpass(input, cutoff) result(output)
        implicit none
        real(kind=8), intent(in) :: input, cutoff
        real(kind=8) :: output
        
        output = input * (1.0_8 - exp(-cutoff))
    end function apply_highpass
    
    ! Simple band-pass filter implementation
    function apply_bandpass(input, center_freq) result(output)
        implicit none
        real(kind=8), intent(in) :: input, center_freq
        real(kind=8) :: output
        
        output = input * sin(center_freq) * exp(-abs(input - center_freq))
    end function apply_bandpass
    
    ! Normalize array to unit variance
    subroutine normalize_array(array, n)
        implicit none
        integer, intent(in) :: n
        real(kind=8), intent(inout) :: array(n)
        
        real(kind=8) :: mean_val, std_val
        
        call calculate_stats(array, n, mean_val, std_val)
        if (std_val > 1.0e-12_8) then
            array = (array - mean_val) / std_val
        end if
    end subroutine normalize_array
    
end module data_processor