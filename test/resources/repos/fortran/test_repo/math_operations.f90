! Mathematical operations module
module math_operations
    implicit none
    
    private
    public :: calculate_mean, calculate_variance, vector_type
    
    ! Derived type definition
    type :: vector_type
        real(kind=8), allocatable :: data(:)
        integer :: length
    contains
        procedure :: initialize => vector_initialize
        procedure :: compute_norm => vector_norm
        procedure :: cleanup => vector_cleanup
    end type vector_type
    
    ! Interface for overloaded procedures
    interface calculate_stats
        module procedure calculate_stats_real
        module procedure calculate_stats_integer
    end interface calculate_stats
    
contains
    
    ! Pure function to calculate mean
    pure function calculate_mean(array, n) result(mean)
        implicit none
        integer, intent(in) :: n
        real(kind=8), intent(in) :: array(n)
        real(kind=8) :: mean
        
        mean = sum(array) / real(n, kind=8)
    end function calculate_mean
    
    ! Elemental function to calculate variance
    elemental function calculate_variance(array, n, mean) result(variance)
        implicit none
        integer, intent(in) :: n
        real(kind=8), intent(in) :: array(n)
        real(kind=8), intent(in) :: mean
        real(kind=8) :: variance
        
        variance = sum((array - mean)**2) / real(n-1, kind=8)
    end function calculate_variance
    
    ! Type-bound procedure: initialize vector
    subroutine vector_initialize(this, size)
        class(vector_type), intent(inout) :: this
        integer, intent(in) :: size
        
        this%length = size
        if (allocated(this%data)) deallocate(this%data)
        allocate(this%data(size))
        this%data = 0.0_8
    end subroutine vector_initialize
    
    ! Type-bound procedure: compute vector norm
    function vector_norm(this) result(norm)
        class(vector_type), intent(in) :: this
        real(kind=8) :: norm
        
        norm = sqrt(sum(this%data**2))
    end function vector_norm
    
    ! Type-bound procedure: cleanup vector
    subroutine vector_cleanup(this)
        class(vector_type), intent(inout) :: this
        
        if (allocated(this%data)) then
            deallocate(this%data)
        end if
        this%length = 0
    end subroutine vector_cleanup
    
    ! Overloaded procedure for real arrays
    subroutine calculate_stats_real(array, n, mean, std_dev)
        implicit none
        integer, intent(in) :: n
        real(kind=8), intent(in) :: array(n)
        real(kind=8), intent(out) :: mean, std_dev
        real(kind=8) :: variance
        
        mean = calculate_mean(array, n)
        variance = calculate_variance(array, n, mean)
        std_dev = sqrt(variance)
    end subroutine calculate_stats_real
    
    ! Overloaded procedure for integer arrays
    subroutine calculate_stats_integer(array, n, mean, std_dev)
        implicit none
        integer, intent(in) :: n
        integer, intent(in) :: array(n)
        real(kind=8), intent(out) :: mean, std_dev
        real(kind=8) :: real_array(n), variance
        
        real_array = real(array, kind=8)
        mean = calculate_mean(real_array, n)
        variance = calculate_variance(real_array, n, mean)
        std_dev = sqrt(variance)
    end subroutine calculate_stats_integer
    
end module math_operations